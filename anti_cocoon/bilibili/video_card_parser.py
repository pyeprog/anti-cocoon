from anti_cocoon.bilibili.video_card import VideoCard


from playwright.async_api._generated import Locator


from contextlib import suppress
from datetime import datetime, timedelta


class VideoCardParser:
    def __init__(self, video_card: VideoCard, timeout: int = 3000) -> None:
        self._video_card = video_card
        self._timeout = timeout

    @classmethod
    def from_locator(cls, video_card: Locator, timeout: int = 3000):
        return cls(VideoCard(video_card), timeout=timeout)

    async def _text(self, async_func, default="") -> str:
        _text = default

        # with suppress(Exception):
        _text = await async_func()

        assert isinstance(_text, str)
        return _text.strip()

    async def link(self) -> str:
        async def _():
            return await self._video_card.link.get_attribute("href", timeout=self._timeout)

        return await self._text(_)

    async def title(self) -> str:
        async def _():
            return await self._video_card.title.get_attribute("title", timeout=self._timeout)

        return await self._text(_)

    async def author(self) -> str:
        async def _():
            return await self._video_card.author.text_content(timeout=self._timeout)

        return await self._text(_)

    async def date(self) -> datetime:
        async def _():
            return await self._video_card.date.text_content(timeout=self._timeout)

        return self._parse_date_text(await self._text(_))

    async def view(self) -> int:
        async def _():
            return await self._video_card.view.text_content(timeout=self._timeout)

        return self._parse_num_text(await self._text(_, default="0"))

    async def barrage(self) -> int:
        async def _():
            return await self._video_card.barrage.text_content(timeout=self._timeout)

        return self._parse_num_text(await self._text(_, default="0"))

    async def duration(self) -> int:
        async def _():
            return await self._video_card.duration.text_content(timeout=self._timeout)

        return self._parse_duration_text(await self._text(_, default="0"))

    def _parse_date_text(self, date_text: str) -> datetime:
        # Parse date string
        date_str = date_text.strip().lstrip("·").strip()

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

        return date

    def _parse_num_text(self, view_text: str) -> int:
        assert isinstance(view_text, str)
        unit = 10000 if view_text.count("万") else 1
        return int(float(view_text.strip().replace("万", "")) * unit)

    def _parse_duration_text(self, duration_text: str) -> int:
        if not duration_text:
            return 0

        parts = duration_text.strip().split(":")
        duration = 0

        unit = 1
        for part in parts[::-1]:
            duration += int(part) * unit
            unit *= 60

        return duration
