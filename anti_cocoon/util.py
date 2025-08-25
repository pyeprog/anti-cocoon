from pathlib import Path
from playwright.async_api._generated import Locator
from sqlmodel import SQLModel

from sqlmodel import Session, create_engine


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
