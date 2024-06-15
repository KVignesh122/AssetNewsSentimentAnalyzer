import asyncio
import websearch_funcs
import gpt_client

from scrapper import get_news_links, parse_webpage
from datetime import datetime
from gpt_client import chunk, get_gpt_response, ANALYSER_INSTR


class SentimentAnalyzer:
    def __init__(self, asset, openai_key=None, model="gpt-3.5-turbo") -> None:
        self.asset = asset
        self.oai_key = openai_key
        self.model = model

        self.date_of_interest = None
        self.news_links = None
        return

    def fetch_news_links(self, news_date=datetime.today(), nlinks=4):
        if not isinstance(nlinks, int):
            raise ValueError("nlinks parameter value has to be an int.")
        
        if news_date == self.date_of_interest:
            assert(self.news_links is not None)
            return self.news_links
        
        self.date_of_interest = news_date
        self.news_links = get_news_links(self.asset, nlinks, news_date)
        # print(self.news_links[0])
        return self.news_links
    
    def show_news_content(self, news_url):
        return asyncio.run(parse_webpage(news_url))

    async def get_all_news_content(self, links):
        news = ''
        for idx, link in enumerate(links, start=1):
            news += f"""
                Article {idx}:
                "{await parse_webpage(link)}"
                """
        return news
    
    def construct_report_prompt(self, max_words, news):
        return f"""Write out a short and impactful report with key insights 
                for {self.asset} from these given information:
                {news}
                Your writeup must strictly be within {max_words} words.
                """
    
    def produce_daily_report(self, date=datetime.today(), max_words=100):
        if self.oai_key is None:
            raise ValueError("An OpenAI API key is required to interact with GPT models.")
        
        links = self.fetch_news_links(date)
        assert(len(links) <= 4)
        
        news = asyncio.run(self.get_all_news_content(links))
        news = chunk(news)
        text = get_gpt_response(
                user_prompt=self.construct_report_prompt(max_words, news),
                openai_key=self.oai_key,
                preferred_model=self.model
            )
        return text

    def construct_sentiment_prompt(self, news):
        return f"""Based on all your knowlege of financial markets and textual analysis, 
            assess information from all these articles and determine if the sentiment for {self.asset} 
            is mainly bullish, bearish, or neutral:
            {news}
            Your response must strictly contain only one word string in lower case ("bullish", "bearish", 
            or "neutral") and no other words.
            """
    
    def get_sentiment(self, date=datetime.today()):
        if self.oai_key is None:
            raise ValueError("An OpenAI API key is required to interact with GPT models.")

        links = self.fetch_news_links(date)
        assert(len(links) <= 4)
        
        news = asyncio.run(self.get_all_news_content(links))
        news = chunk(news)
        sentiment = get_gpt_response(
            user_prompt=self.construct_sentiment_prompt(news),
            openai_key=self.oai_key,
            generation_tk_limit=10,
            preferred_model=self.model,
            system_instruction=ANALYSER_INSTR
        )
        return sentiment.lower()


class WebInteractor():
    def __init__(self) -> None:
        pass

    def search_google(self, query, tld='com', lang='en', date='0', country='', tab='', nlinks=None):
        links =  list(websearch_funcs.search_google(
            query=query,
            tld=tld,
            lang=lang,
            tbs=websearch_funcs.get_tbs(date),
            country=country,
            tbm=tab,
            stop=nlinks
        ))
        return list(set(links))
    
    def get_webpage_main_content(self, url):
        return asyncio.run(parse_webpage(url))
    
    def get_llm_response(self, prompt, openai_api_key, generation_tk_limit=None, gpt_model="gpt-3.5-turbo", system_instruction=None):
        return gpt_client.get_gpt_response(
                user_prompt=prompt,
                openai_key=openai_api_key,
                generation_tk_limit=generation_tk_limit,
                preferred_model=gpt_model,
                system_instruction=system_instruction
            )
