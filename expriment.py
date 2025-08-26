import asyncio
import json
from pprint import pprint

from bilibili_api.search import search


if __name__ == "__main__":
    _json = asyncio.run(search(keyword="AI入门", page=1))
    with open("experiment.json", "w", encoding="utf-8") as fp:
        json.dump(_json, fp)
