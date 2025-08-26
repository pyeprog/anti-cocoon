from playwright.async_api._generated import Locator


class VideoCard:
    def __init__(self, video_card: Locator):
        self._video_card = video_card

    @property
    def link(self):
        return self._video_card.locator('a[target="_blank"]').first

    @property
    def title(self):
        return self._video_card.locator("h3.bili-video-card__info--tit")

    @property
    def author(self):
        return self._video_card.locator("span.bili-video-card__info--author")

    @property
    def date(self):
        return self._video_card.locator("span.bili-video-card__info--date")

    @property
    def view(self):
        return self._video_card.locator("span.bili-video-card__stats--item").nth(0)

    @property
    def barrage(self):
        return self._video_card.locator("span.bili-video-card__stats--item").nth(1)

    @property
    def duration(self):
        return self._video_card.locator("span.bili-video-card__stats__duration")
