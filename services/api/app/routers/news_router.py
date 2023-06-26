from fastapi import Depends
from app.domain.services.news_service import NewsService, create_news_service
from .api_router import APIRouter

router = APIRouter(prefix="/news")


@router.get("/")
async def get_news(
    service: NewsService = Depends(create_news_service)
):
    return service.get_news()
