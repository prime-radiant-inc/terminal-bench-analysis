# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx", "tqdm"]
# ///

import argparse
import asyncio
import os
from pathlib import Path

import httpx

REPO_ID = "harborframework/terminal-bench-2-leaderboard"
API_URL = f"https://huggingface.co/api/datasets/{REPO_ID}"
RAW_BASE = f"https://huggingface.co/datasets/{REPO_ID}/resolve/main"


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
        resp = await client.get(url)
        resp.raise_for_status()
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
            resp = await client.get(url)
            resp.raise_for_status()
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
    args = parser.parse_args()

    num_workers = 8
    sem = asyncio.Semaphore(num_workers)
    queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=64)
    downloaded: list[str] = []

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        print("Fetching file list and downloading...")

        # Start the producer
        producer = asyncio.create_task(produce_files(client, queue, args.stop_after))

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

        print(
            f"Found {total_found} result.json files, "
            f"downloaded {len(downloaded)} new files"
        )


if __name__ == "__main__":
    asyncio.run(main())
