

import html
from pydantic import BaseModel
import feedparser


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
        url = "https://cflnewshub.com/feed/"  # rss
        feed = feedparser.parse(url)

        news_items = []
        for entry in feed.entries:
            news_items.append(NewsItem(
                title=entry.title,
                link=entry.link,
                pub_date=entry.published,
                description=self._parse_description(entry.description),
                guid=entry.guid
            ))

        return news_items

    def _parse_description(self, description: str) -> str:
        description = description.split("<p>")[1].split("</p>")[0]
        description = html.unescape(description)
        description = description.replace("[…]", "…")
        return description


def create_news_service() -> NewsService:
    return NewsService()
