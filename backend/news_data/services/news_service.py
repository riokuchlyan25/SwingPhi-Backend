# internal
from news_data.config import NEWS_API_KEY

# external
from newsapi import NewsApiClient

# built-in
from django.http import JsonResponse

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

def get_top_headlines(query: str):
    articles = newsapi.get_everything(
        q=query,
        language='en',
        sort_by='relevancy',
        page_size=10  # Limit to 10 most relevant articles
    )
    return JsonResponse(articles)
