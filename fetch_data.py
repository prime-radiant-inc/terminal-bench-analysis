# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx", "tqdm"]
# ///

import argparse
import asyncio
import json
import os
from pathlib import Path

import httpx

REPO_ID = "harborframework/terminal-bench-2-leaderboard"
API_URL = f"https://huggingface.co/api/datasets/{REPO_ID}"
RAW_BASE = f"https://huggingface.co/datasets/{REPO_ID}/resolve/main"


async def fetch_file_list(client: httpx.AsyncClient) -> list[str]:
    resp = await client.get(API_URL)
    resp.raise_for_status()
    siblings = resp.json()["siblings"]
    return [s["rfilename"] for s in siblings if s["rfilename"].endswith("result.json")]


async def download_file(
    client: httpx.AsyncClient, sem: asyncio.Semaphore, rfilename: str
) -> str:
    url = f"{RAW_BASE}/{rfilename}"
    dest = Path(rfilename)
    dest.parent.mkdir(parents=True, exist_ok=True)
    async with sem:
        resp = await client.get(url)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
    return rfilename


async def main():
    parser = argparse.ArgumentParser(
        description="Mirror result.json files from HF repo"
    )
    parser.add_argument("--progress", action="store_true", help="Show progress bar")
    parser.add_argument(
        "--stop-after", type=int, default=None, help="Stop after N files"
    )
    args = parser.parse_args()

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        print("Fetching file list...")
        files = await fetch_file_list(client)
        print(f"Found {len(files)} result.json files")

        # Filter out already downloaded
        to_download = [f for f in files if not Path(f).exists()]
        print(
            f"{len(files) - len(to_download)} already downloaded, {len(to_download)} remaining"
        )

        if args.stop_after is not None:
            to_download = to_download[: args.stop_after]
            print(f"Limiting to {len(to_download)} files (--stop-after)")

        if not to_download:
            print("Nothing to download.")
            return

        sem = asyncio.Semaphore(8)

        if args.progress:
            from tqdm.asyncio import tqdm_asyncio

            tasks = [download_file(client, sem, f) for f in to_download]
            await tqdm_asyncio.gather(*tasks, desc="Downloading")
        else:
            tasks = [download_file(client, sem, f) for f in to_download]
            await asyncio.gather(*tasks)

        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
