from scrapper import get_news_links, parse_webpage
from datetime import datetime
import tracemalloc
import asyncio
from gpt_client import chunk, get_gpt_response, ANALYSER_INSTR
from oai import MY_KEY


class SentimentAnalyzer:
    def __init__(self, asset, openai_key=None) -> None:
        self.asset = asset
        self.oai_key = openai_key
        return

    def fetch_news_links(self, news_date=datetime.today()):
        return get_news_links(self.asset, news_date)
    
    def show_news_content(self, news_url):
        return asyncio.run(parse_webpage(news_url))

    async def get_news_content(self, links):
        news = ''
        for idx, link in enumerate(links, start=1):
            news += f"""
                Article {idx}:
                "{await parse_webpage(link)}"
                """
        return news
    
    def produce_daily_report(self, date=datetime.today(), max_words=100):
        links = get_news_links(self.asset, date)
        assert(len(links) <= 4)
        
        news = asyncio.run(self.get_news_content(links))
        news = chunk(news)
        text = get_gpt_response(
                user_prompt=f"""Write out a short and impactful report with key insights 
                for {self.asset} from these given information:
                {news}
                Your writeup must strictly be within {max_words} words.
                """,
                openai_key=self.oai_key,
                preferred_model="gpt-4o"
            )
        return text
    
    def get_sentiment(self, date=datetime.today()):
        links = get_news_links(self.asset, date)
        assert(len(links) <= 4)
        
        news = asyncio.run(self.get_news_content(links))
        news = chunk(news)
        sentiment = get_gpt_response(
            user_prompt=f"""Based on all your knowlege of financial markets and textual analysis, 
            assess information from all these articles and determine if the sentiment for {self.asset} 
            is mainly bullish, bearish, or neutral:
            {news}
            Your response must strictly contain only one word string in lower case ("bullish", "bearish", 
            or "neutral") and no other words.
            """,
            openai_key=self.oai_key,
            generation_tk_limit=5,
            # preferred_model="gpt-4o",
            system_instruction=ANALYSER_INSTR
        )
        return sentiment.lower()


# analyser = SentimentAnalyzer("EURUSD", MY_KEY)
# # analyser.fetch_news_links(news_date="06/06/2024")
# # foo = analyser.produce_daily_report(news_date="06/06/2024")
# foo = analyser.get_sentiment(date="06/06/2024")
# print(foo)
# # https://www.equiti.com/sc-en/news/trade-reviews/the-sp-500-index-reached-its-highest-peak-of-the-year/

