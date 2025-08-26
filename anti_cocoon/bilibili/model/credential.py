import json
from pathlib import Path
from pydantic import BaseModel, Field


class Credential(BaseModel):
    sessdata: str = Field(default="")
    bili_jct: str = Field(default="")
    buvid3: str = Field(default="")
    buvid4: str = Field(default="")
    dedeuserid: str = Field(default="")
    ac_time_value: str = Field(default="")

    @classmethod
    def from_file(cls, json_file_path: str | Path):
        json_file_path = Path(json_file_path) if isinstance(json_file_path, str) else json_file_path
        if not json_file_path.exists():
            raise FileNotFoundError(f"{json_file_path} is not valid file path")

        with open(json_file_path, "r") as fp:
            context_storage: dict = json.load(fp)

        cookies: dict[str, str] = {
            c["name"]: c["value"] for c in context_storage["cookies"] if c["domain"] == ".bilibili.com"
        }
        local_storage: list[dict] = {cs["origin"]: cs["localStorage"] for cs in context_storage["origins"]}.get(
            "https://www.bilibili.com", {}
        )

        return cls(
            sessdata=cookies["SESSDATA"],
            bili_jct=cookies["bili_jct"],
            buvid3=cookies["buvid3"],
            buvid4=cookies["buvid4"],
            dedeuserid=cookies["DedeUserID"],
            ac_time_value={d["name"]: d["value"] for d in local_storage}.get("ac_time_value", ""),
        )
