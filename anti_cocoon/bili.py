import asyncio
from contextlib import suppress

from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4, uuid5

from playwright.async_api import async_playwright
from playwright.async_api._generated import Locator
from pydantic.functional_validators import model_validator
from sqlmodel import SQLModel, Field

from anti_cocoon.util import safe_all


class BiliSearch:
    BILI_VIDEO_NS = UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8")

    class BiliVideo(SQLModel, table=True):
        title: str = Field(default="", primary_key=True)
        link: str = Field(default="")
        author: str = Field(default="", index=True)
        date: datetime = Field(index=True, default_factory=datetime.now)
        n_views: int = Field(default=0)
        n_barrages: int = Field(default=0)
        duration_sec: int = Field(default=0)

        @model_validator(mode="after")
        def check_title(self):
            if not self.title:
                raise ValueError("title should not be empty")
            return self

    def __init__(
        self, context_storage: Path | None = None, headless: bool = True
    ) -> None:
        self._headless = headless
        self._context_storage = context_storage

    async def extract_stats(
        self, bili_video_card_wrap: Locator, timeout: int = 3000
    ) -> tuple[int, int, int]:
        stats_elem = bili_video_card_wrap.locator("div.bili-video-card__stats")

        stats_item_elems = await safe_all(
            stats_elem.locator("span.bili-video-card__stats--item"), timeout=timeout
        )

        match (len(stats_item_elems)):
            case 0:
                raise LookupError
            case 1:
                views = await stats_item_elems[0].text_content(timeout=timeout)
                barrages = "0"
            case 2:
                views = await stats_item_elems[0].text_content(timeout=timeout)
                barrages = await stats_item_elems[1].text_content(timeout=timeout)

        assert isinstance(views, str)
        unit = 10000 if views.count("万") else 1
        views = int(float(views.strip().replace("万", "")) * unit)

        assert isinstance(barrages, str)
        barrages = int(barrages.strip().replace("万", "0000"))

        duration_str = await stats_elem.locator(
            "span.bili-video-card__stats__duration"
        ).text_content(timeout=timeout)
        assert isinstance(duration_str, str)

        parts = duration_str.strip().split(":")
        unit = 1
        duration = 0
        for part in parts[::-1]:
            duration += int(part) * unit
            unit *= 60

        return views, barrages, duration

    async def extract_info(
        self, bili_video_card_wrap: Locator, timeout: int = 3000
    ) -> tuple[str, str, datetime]:
        info_elem = bili_video_card_wrap.locator("div.bili-video-card__info")

        title = await info_elem.locator("h3.bili-video-card__info--tit").get_attribute(
            "title", timeout=timeout
        )

        author = await info_elem.locator(
            "span.bili-video-card__info--author"
        ).text_content(timeout=timeout)

        date = ""
        with suppress(Exception):
            date = await info_elem.locator(
                "span.bili-video-card__info--date"
            ).text_content(timeout=timeout)

        # Parse date string
        assert isinstance(date, str)
        date_str = date.strip().lstrip("·").strip()

        date = datetime.now()
        if "分钟前" in date_str:
            minutes = int(date_str.replace("分钟前", "").strip())
            date = datetime.now() - timedelta(minutes=minutes)
        elif "小时前" in date_str:
            hours = int(date_str.replace("小时前", "").strip())
            date = datetime.now() - timedelta(hours=hours)
        elif "-" in date_str:
            # Handle '07-14' or '2024-07-14'
            parts = date_str.split("-")
            if len(parts) == 2:
                # Format: MM-DD, assume current year
                year = datetime.now().year
                month, day = map(int, parts)
                date = datetime(year, month, day)
            elif len(parts) == 3:
                # Format: YYYY-MM-DD
                year, month, day = map(int, parts)
                date = datetime(year, month, day)
        else:
            # Fallback: try to parse as full date
            with suppress(Exception):
                date = datetime.strptime(date_str, "%Y-%m-%d")

        assert isinstance(title, str)
        assert isinstance(author, str)

        return title.strip(), author.strip(), date

    async def extract_link(self, bili_video_card_wrap, timeout: int = 3000) -> str:
        link_str = ""

        link_str = await bili_video_card_wrap.locator(
            'a[target="_blank"]'
        ).first.get_attribute("href", timeout=timeout)

        assert isinstance(link_str, str)

        return link_str.strip()

    async def process_card(self, card_elem: Locator):
        try:
            views, barrages, duration_sec = await self.extract_stats(card_elem)
            link_str = await self.extract_link(card_elem)
            title, author, date = await self.extract_info(card_elem)
            return self.BiliVideo(
                title=title,
                link=link_str,
                author=author,
                date=date,
                n_views=views,
                n_barrages=barrages,
                duration_sec=duration_sec,
            )
        except:
            return None

    async def on(self, keyword: str, n_pages: int = 1) -> list[BiliVideo]:
        items: list[BiliSearch.BiliVideo] = []

        async with async_playwright() as player:
            browser = await player.chromium.launch(headless=self._headless)
            context = await browser.new_context(storage_state=self._context_storage)

            home_page = await context.new_page()
            await home_page.goto("https://www.bilibili.com")

            await home_page.locator("input.nav-search-input").fill(keyword)

            async with context.expect_page() as new_page_info:
                await home_page.locator("div.nav-search-btn").click()

            search_page = await new_page_info.value

            for i in range(n_pages):
                print(f"working on page {i + 1}")
                card_elems = await safe_all(
                    search_page.locator("div.video-list >> div.bili-video-card__wrap"),
                    timeout=3000,
                )

                results = await asyncio.gather(
                    *(self.process_card(card_elem) for card_elem in card_elems)
                )

                items.extend(list(filter(bool, results)))  # type: ignore

                next_button = search_page.locator(
                    "div.vui_pagenation--btns >> button"
                ).last
                await next_button.click(timeout=3000)

        print(f"done working, {len(items)} collected")
        return items
