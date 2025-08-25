import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright

from anti_cocoon.bilibili.model.video import Video
from anti_cocoon.bilibili.search_page import SearchPage
from anti_cocoon.bilibili.video_card import VideoCard
from anti_cocoon.bilibili.video_card_parser import VideoCardParser


async def video_card_to_video(video_card: VideoCard, source: str = "search", timeout: int = 3000) -> Optional[Video]:
    parser = VideoCardParser(video_card, timeout=timeout)

    try:
        title, link, author, release_date, n_views, n_barrages, duration_sec = await asyncio.gather(
            parser.title(),
            parser.link(),
            parser.author(),
            parser.date(),
            parser.view(),
            parser.barrage(),
            parser.duration(),
        )

        assert isinstance(title, str)
        assert isinstance(link, str)
        assert isinstance(author, str)
        assert isinstance(release_date, datetime)
        assert isinstance(n_views, int)
        assert isinstance(n_barrages, int)
        assert isinstance(duration_sec, int)

        return Video(
            title=title,
            link=link,
            author=author,
            release_date=release_date,
            collect_date=datetime.now(),
            n_views=n_views,
            n_barrages=n_barrages,
            duration_sec=duration_sec,
            source=source,
        )

    except Exception:
        return None


class BiliApp:
    def __init__(self, context_storage: Path | None = None, headless: bool = True, timeout: int = 3000) -> None:
        self._headless = headless
        self._context_storage = context_storage
        self._player_context = async_playwright()
        self._timeout = timeout

    @asynccontextmanager
    async def context(self):
        player = await self._player_context.__aenter__()
        browser = await player.chromium.launch(headless=self._headless)
        try:
            yield await browser.new_context(storage_state=self._context_storage)
        finally:
            await self._player_context.__aexit__()

    async def search_page(self, context, keyword: str) -> SearchPage:
        home_page = await context.new_page()
        await home_page.goto("https://www.bilibili.com")

        await home_page.locator("input.nav-search-input").fill(keyword)

        async with context.expect_page() as new_page_info:
            await home_page.locator("div.nav-search-btn").click()

        return SearchPage(await new_page_info.value, timeout=self._timeout)

    async def search_videos(self, keyword: str, n_page: int = 5):
        print(f"search on {keyword}")
        videos: list[Video] = []

        async with self.context() as context:
            search_page = await self.search_page(context, keyword)

            for i in range(n_page):
                print(f"working on page {i + 1}")

                cur_videos = await asyncio.gather(
                    *[video_card_to_video(video_card) for video_card in await search_page.video_cards()]
                )

                videos.extend(list(filter(bool, cur_videos)))  # type: ignore

                await search_page.to_next_page()

        print(f"done working, {len(videos)} collected")
        return videos
