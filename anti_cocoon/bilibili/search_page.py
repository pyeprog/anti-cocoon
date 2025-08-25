from playwright.async_api._generated import Page

from anti_cocoon.bilibili.video_card import VideoCard
from anti_cocoon.util import safe_all


class SearchPage:
    def __init__(self, page: Page, timeout: int = 3000):
        self._page = page
        self._timeout = timeout

    async def to_next_page(self):
        await self._page.locator("div.vui_pagenation--btns >> button").last.click(timeout=self._timeout)

    async def video_cards(self) -> list[VideoCard]:
        return [
            VideoCard(elem)
            for elem in await safe_all(
                self._page.locator("div.video-list >> div.bili-video-card__wrap"), timeout=self._timeout
            )
        ]

    async def video_cards_iter(self):
        for elem in await safe_all(
            self._page.locator("div.video-list >> div.bili-video-card__wrap"), timeout=self._timeout
        ):
            yield VideoCard(elem)
