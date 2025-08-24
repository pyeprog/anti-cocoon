import asyncio
from pathlib import Path
import time

from dateutil.utils import today

from anti_cocoon.bili import BiliSearch
from anti_cocoon.util import dump


def fetch_from_bili(keyword: str, n_pages: int = 3):
    results = asyncio.run(
        BiliSearch(context_storage=Path(".context/bili.json"), headless=True).on(
            keyword=keyword,
            n_pages=n_pages,
        )
    )

    dump("./.data/bili.sqlite.db", results)  # type: ignore


def main():
    print(f"schedule job runs on {today()}")
    fetch_from_bili("AI agent", 3)
    fetch_from_bili("AI框架", 3)
    fetch_from_bili("AI", 3)


if __name__ == "__main__":
    import schedule

    schedule.every(1).days.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
