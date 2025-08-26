from pathlib import Path
import re
from playwright.async_api._generated import Locator
from sqlmodel import SQLModel

from sqlmodel import Session, create_engine


def parse_duration_text(duration_text: str) -> int:
    if not duration_text:
        return 0

    parts = duration_text.strip().split(":")
    duration = 0

    unit = 1
    for part in parts[::-1]:
        duration += int(part) * unit
        unit *= 60

    return duration


async def safe_all(loc: Locator, timeout: int = 3000):
    try:
        await loc.first.wait_for(state="visible", timeout=timeout)
        return await loc.all()
    except Exception:
        return []


def dump(db_path: str, data: list[SQLModel]):
    Path(db_path).touch(exist_ok=True)
    if not db_path.startswith("sqlite:///"):
        db_path = "sqlite:///" + db_path

    engine = create_engine(db_path)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        for item in data:
            session.merge(item)

        session.commit()


def remove_html_tag(text: str) -> str:
    # Remove HTML tags using regex
    clean_text = re.sub(r"<[^>]+>", "", text)
    # Remove extra whitespace
    return clean_text.strip()
