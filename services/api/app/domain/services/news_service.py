import html
import time
from functools import lru_cache

import feedparser
from pydantic import BaseModel


class NewsItem(BaseModel):
    title: str
    link: str
    pub_date: str
    description: str
    guid: str


class NewsService:
    def __init__(self):
        pass

    def get_news(self) -> list[NewsItem]:
        return _get_news(get_ttl_hash())


def get_ttl_hash(seconds=900):
    return round(time.time() / seconds)


@lru_cache()
def _get_news(ttl_hash=None) -> list[NewsItem]:
    url = "https://cflnewshub.com/feed/"  # rss
    feed = feedparser.parse(url)

    news_items = []
    for entry in feed.entries:
        news_items.append(
            NewsItem(
                title=entry.title,
                link=entry.link,
                pub_date=entry.published,
                description=_parse_description(entry.description),
                guid=entry.guid,
            )
        )

    return news_items


def _parse_description(description: str) -> str:
    description = description.split("<p>")[1].split("</p>")[0]
    description = html.unescape(description)
    description = description.replace("[…]", "…")
    return description


def create_news_service() -> NewsService:
    return NewsService()
