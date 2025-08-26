import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from bilibili_api.search import search
from playwright.async_api import async_playwright

from anti_cocoon.bilibili.model.video import Video
from anti_cocoon.bilibili.pom.search_page import SearchPage
from anti_cocoon.bilibili.pom.util.video_card_to_video import video_card_to_video
from anti_cocoon.util import parse_duration_text, remove_html_tag


class Search:
    def __init__(self, context_storage: Path | None = None, headless: bool = True, timeout: int = 3000) -> None:
        self._headless = headless
        self._context_storage = context_storage
        self._player_context = async_playwright()
        self._timeout = timeout

    @asynccontextmanager
    async def _context(self):
        player = await self._player_context.__aenter__()
        browser = await player.chromium.launch(headless=self._headless)
        try:
            yield await browser.new_context(storage_state=self._context_storage)
        finally:
            await self._player_context.__aexit__()

    async def _search_page(self, context, keyword: str) -> SearchPage:
        home_page = await context.new_page()
        await home_page.goto("https://www.bilibili.com")

        await home_page.locator("input.nav-search-input").fill(keyword)

        async with context.expect_page() as new_page_info:
            await home_page.locator("div.nav-search-btn").click()

        return SearchPage(await new_page_info.value, timeout=self._timeout)

    async def videos(self, keyword: str, n_page: int = 5) -> list[Video]:
        print(f"search on {keyword}")
        videos: list[Video] = []

        async with self._context() as context:
            search_page = await self._search_page(context, keyword)

            for i in range(n_page):
                print(f"working on page {i + 1}")

                cur_videos = await asyncio.gather(
                    *[video_card_to_video(video_card) for video_card in await search_page.video_cards()]
                )

                videos.extend(list(filter(bool, cur_videos)))  # type: ignore

                await search_page.to_next_page()

        print(f"done working, {len(videos)} collected")
        return videos


class ApiSearch:
    def __init__(self, delay_between_pages: int = 1000):
        self._delay = delay_between_pages

    def _parse(self, video_detail: dict) -> list[Video]:
        video_jsons: list[dict] = {res["result_type"]: res["data"] for res in video_detail["result"]}.get("video", [])

        videos: list[Video] = []
        for video_json in video_jsons:
            videos.append(
                Video(
                    title=remove_html_tag(video_json["title"]),
                    link=f"//www.bilibili.com/video/{video_json['bvid']}/",
                    author=video_json["author"],
                    release_date=datetime.fromtimestamp(video_json["pubdate"]),
                    collect_date=datetime.now(),
                    n_views=video_json.get("play", 0),
                    n_barrages=video_json.get("danmaku", 0),
                    duration_sec=parse_duration_text(video_json.get("duration", "0")),
                    source="search",  # constant
                )
            )

        return videos

    async def videos(self, keyword: str, n_page: int = 5) -> list[Video]:
        print(f"search on {keyword}")

        videos: list[Video] = []

        for page in range(1, n_page + 1):
            print(f"working on page {page}")
            video_detail: dict = await search(keyword=keyword, page=page)
            videos.extend(self._parse(video_detail))
            await asyncio.sleep(self._delay / 1000)

        print(f"done working, {len(videos)} collected")
        return videos
