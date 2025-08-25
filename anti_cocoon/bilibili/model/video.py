from datetime import datetime
from pydantic import model_validator
from sqlmodel import Field, SQLModel


class Video(SQLModel, table=True):
    title: str = Field(default="", primary_key=True)
    link: str = Field(default="")
    author: str = Field(default="", index=True)
    release_date: datetime = Field(index=True, default_factory=datetime.now)
    collect_date: datetime = Field(index=True, default_factory=datetime.now)
    n_views: int = Field(default=0)
    n_barrages: int = Field(default=0)
    duration_sec: int = Field(default=0)
    source: str = Field(default="search", index=True)  # search

    @model_validator(mode="after")
    def check_title(self):
        if not self.title:
            raise ValueError("title should not be empty")
        return self
