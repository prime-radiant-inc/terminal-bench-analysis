# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx", "tqdm"]
# ///

import argparse
import asyncio
import re
import os
from pathlib import Path

import httpx

REPO_ID = "harborframework/terminal-bench-2-leaderboard"
API_URL = f"https://huggingface.co/api/datasets/{REPO_ID}"
RAW_BASE = f"https://huggingface.co/datasets/{REPO_ID}/resolve/main"
LAST_SHA_FILE = Path("last_fetch_sha.txt")

# Lock + event used to pause all requests when rate-limited.
# Only the first task to hit a 429 sleeps; others wait on the event.
_rate_limit_lock = asyncio.Lock()
_rate_limit_ok = asyncio.Event()
_rate_limit_ok.set()


def _parse_retry_seconds(resp: httpx.Response) -> float:
    """Extract how long to wait from a 429 response."""
    # Standard header first
    retry_after = resp.headers.get("retry-after")
    if retry_after:
        try:
            return float(retry_after)
        except ValueError:
            pass
    # HF-style: ratelimit: "api";r=0;t=178  (t = seconds left in window)
    rl = resp.headers.get("ratelimit", "")
    m = re.search(r"t=(\d+)", rl)
    if m:
        return float(m.group(1))
    return 60.0  # fallback


async def _rate_limited_get(
    client: httpx.AsyncClient, url: str
) -> httpx.Response:
    """GET with global rate-limit pausing."""
    while True:
        await _rate_limit_ok.wait()
        resp = await client.get(url)
        if resp.status_code != 429:
            resp.raise_for_status()
            return resp
        # First task to grab the lock does the sleeping
        async with _rate_limit_lock:
            if _rate_limit_ok.is_set():
                _rate_limit_ok.clear()
                wait = _parse_retry_seconds(resp)
                print(f"Rate limited — pausing all requests for {wait:.0f}s")
                await asyncio.sleep(wait)
                _rate_limit_ok.set()


async def get_head_sha(client: httpx.AsyncClient) -> str:
    """Get the SHA of the latest commit on main."""
    resp = await _rate_limited_get(client, f"{API_URL}/commits/main?limit=1")
    return resp.json()[0]["id"]


async def produce_files_incremental(
    client: httpx.AsyncClient,
    queue: asyncio.Queue,
    old_sha: str,
    new_sha: str,
):
    """Use the compare API to find result.json files added since old_sha."""
    url = f"{API_URL}/compare/{old_sha}..{new_sha}?raw=true"
    print(f"Comparing {old_sha[:12]}..{new_sha[:12]}")
    resp = await _rate_limited_get(client, url)
    found = 0
    queued = 0
    for line in resp.text.strip().splitlines():
        path = line.split("\t")[-1]
        if path.endswith("result.json"):
            found += 1
            if not Path(path).exists():
                await queue.put(path)
                queued += 1
    await queue.put(None)
    print(f"Found {found} result.json files in diff ({queued} new)")
    return found


async def produce_files(
    client: httpx.AsyncClient,
    queue: asyncio.Queue,
    stop_after: int | None,
):
    """Page through the tree API and push new files onto the queue."""
    url = f"{API_URL}/tree/main?recursive=true&limit=1000"
    found = 0
    queued = 0
    while url:
        print(f"Fetching page: {url}")
        resp = await _rate_limited_get(client, url)
        for item in resp.json():
            path = item["path"]
            if path.endswith("result.json"):
                found += 1
                if not Path(path).exists():
                    if stop_after is not None and queued >= stop_after:
                        await queue.put(None)
                        return found
                    await queue.put(path)
                    queued += 1
        # Cursor-based pagination via Link header
        link = resp.headers.get("link", "")
        url = None
        if 'rel="next"' in link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.split("<")[1].split(">")[0]
                    break
    await queue.put(None)
    return found


async def download_worker(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    queue: asyncio.Queue,
    downloaded: list[str],
):
    """Pull paths from the queue and download them."""
    while True:
        path = await queue.get()
        if path is None:
            queue.task_done()
            break
        url = f"{RAW_BASE}/{path}"
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        async with sem:
            resp = await _rate_limited_get(client, url)
            dest.write_bytes(resp.content)
        downloaded.append(path)
        queue.task_done()


async def main():
    parser = argparse.ArgumentParser(
        description="Mirror result.json files from HF repo"
    )
    parser.add_argument("--progress", action="store_true", help="Show progress bar")
    parser.add_argument(
        "--stop-after", type=int, default=None, help="Stop after N files"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Only fetch files added since last run (uses last_fetch_sha.txt)",
    )
    args = parser.parse_args()

    num_workers = 8
    sem = asyncio.Semaphore(num_workers)
    queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=64)
    downloaded: list[str] = []

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        if args.update:
            if not LAST_SHA_FILE.exists():
                print(f"Error: {LAST_SHA_FILE} not found. Run a full fetch first.")
                return
            old_sha = LAST_SHA_FILE.read_text().strip()
            new_sha = await get_head_sha(client)
            if old_sha == new_sha:
                print("Already up to date.")
                return
            print(f"Fetching files added since {old_sha[:12]}...")
            producer = asyncio.create_task(
                produce_files_incremental(client, queue, old_sha, new_sha)
            )
        else:
            print("Fetching full file list and downloading...")
            producer = asyncio.create_task(
                produce_files(client, queue, args.stop_after)
            )
            new_sha = await get_head_sha(client)

        # Start download workers
        workers = []
        for _ in range(num_workers):
            workers.append(
                asyncio.create_task(download_worker(client, sem, queue, downloaded))
            )

        # Wait for the producer to finish listing
        total_found = await producer

        # Send poison pills for remaining workers (producer already sent one)
        for _ in range(num_workers - 1):
            await queue.put(None)

        await asyncio.gather(*workers)

        # Save the SHA we fetched up to
        LAST_SHA_FILE.write_text(new_sha + "\n")

        print(
            f"Found {total_found} result.json files, "
            f"downloaded {len(downloaded)} new files"
        )


if __name__ == "__main__":
    asyncio.run(main())
