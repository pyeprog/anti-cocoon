import asyncio
from datetime import datetime
from pathlib import Path
import time


from anti_cocoon.bilibili.app import BiliApp
from anti_cocoon.util import dump


async def search_from_bili(keyword: str, n_pages: int = 3, do_dump: bool = True):
    results = await BiliApp(context_storage=Path(".context/bili.json"), headless=True, timeout=5000).search_videos(
        keyword=keyword, n_page=n_pages
    )

    if do_dump:
        dump("./.data/bili.sqlite.db", results)  # type: ignore


def main():
    print(f"schedule job runs on {datetime.now()}")

    async def _():
        await search_from_bili("AI agent", 3)
        await search_from_bili("AI框架", 3)
        await search_from_bili("AI大模型", 3)

    asyncio.run(_())


if __name__ == "__main__":
    import schedule

    schedule.every(5).minutes.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
