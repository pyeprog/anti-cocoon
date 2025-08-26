from typing import Optional
from anti_cocoon.bilibili.model.video import Video
from anti_cocoon.bilibili.pom.util.video_card_parser import VideoCardParser
from anti_cocoon.bilibili.pom.video_card import VideoCard


import asyncio
from datetime import datetime


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
