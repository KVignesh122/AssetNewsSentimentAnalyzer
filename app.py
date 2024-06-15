import asyncio
import websearch_funcs

from scrapper import get_news_links, parse_webpage
from datetime import datetime
from gpt_client import chunk, get_gpt_response, ANALYSER_INSTR


class SentimentAnalyzer:
    def __init__(self, asset, openai_key=None, model="gpt-3.5-turbo") -> None:
        """
        Initializes the SentimentAnalyzer object.
        
        Parameters:
            asset (str): The financial asset for which sentiment analysis is to be performed.
            openai_key (str, optional): The API key for OpenAI, required for accessing GPT models.
            model (str, optional): The specific GPT model to use for generating text and analyzing sentiment.
        
        Returns:
            None
        """
        self.asset = asset
        self.oai_key = openai_key
        self.model = model

        self.date_of_interest = None
        self.news_links = None
        return

    def fetch_news_links(self, news_date=datetime.today(), nlinks=4):
        """
        Fetches a specific number of news links related to the asset on a given date.
        
        Parameters:
            news_date (datetime, optional): The date for which to fetch news links.
            nlinks (int, optional): The maximum number of news links to retrieve.
        
        Returns:
            list: A list of URLs as strings that link to news articles.
        
        Raises:
            ValueError: If 'nlinks' is not an integer.
        """
        if not isinstance(nlinks, int):
            raise ValueError("nlinks parameter value has to be an int.")
        
        if news_date == self.date_of_interest:
            assert(self.news_links is not None)
            return self.news_links
        
        self.date_of_interest = news_date
        self.news_links = get_news_links(self.asset, nlinks, news_date)
        return self.news_links
    
    def show_news_content(self, news_url):
        """
        Fetches and displays the content of a news article from a URL.
        
        Parameters:
            news_url (str): The URL of the news article to fetch content from.
        
        Returns:
            str: The content of the news article.
        """
        return asyncio.run(parse_webpage(news_url))

    async def get_all_news_content(self, links):
        """
        Asynchronously retrieves and concatenates the content from a list of news URLs.
        
        Parameters:
            links (list): A list of news URLs to fetch content from.
        
        Returns:
            str: Concatenated content from all the news articles.
        """
        news = ''
        for idx, link in enumerate(links, start=1):
            news += f"""
                Article {idx}:
                "{await parse_webpage(link)}"\n
                """
        return news
    
    def construct_report_prompt(self, max_words, news):
        return f"""Write out a short and impactful report with key insights 
                for {self.asset} from these given information:
                {news}
                Your writeup must strictly be within {max_words} words.
                """
    
    def produce_daily_report(self, date=datetime.today(), max_words=100):
        """
        Produces a short report based on the news linked to the asset for given date, using the GPT model.
        
        Parameters:
            date (datetime, optional): The date for which the report is produced.
            max_words (int, optional): The maximum number of words in the report.
        
        Returns:
            str: The generated report as a string.
        
        Raises:
            ValueError: If an OpenAI API key is not set.
        """
        if self.oai_key is None:
            raise ValueError("An OpenAI API key is required to interact with GPT models.")
        
        links = self.fetch_news_links(date)
        
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
        """
        Determines the news sentiment for the asset for the given date, using the GPT model.
        
        Parameters:
            date (datetime, optional): The date for which sentiment is assessed.
        
        Returns:
            str: The determined sentiment ('bullish', 'bearish', or 'neutral').
        
        Raises:
            ValueError: If an OpenAI API key is not set.
        """
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
        """
        Initializes the WebInteractor class which provides functionalities 
        for interacting with web content and performing web searches.
        """
        pass

    def search_google(self, query, tld='com', lang='en', date='0', country='', tab='', nlinks=None):
        """
        Searches Google for the specified query and retrieves a list of unique links.

        Parameters:
            query (str): The search query.
            tld (str, optional): The top-level domain for Google (e.g., 'com' for Google.com).
            lang (str, optional): The language setting for the Google search.
            date (str, optional): The date to refine search results.
            country (str, optional): The country setting for Google search results.
            tab (str, optional): Specifies the tab under which the search is performed, allowing for specific types of search results.
            Possible values include:
                - 'app' for Applications
                - 'blg' for Blogs
                - 'bks' for Books
                - 'dsc' for Discussions
                - 'isch' for Images
                - 'nws' for News
                - 'pts' for Patents
                - 'plcs' for Places
                - 'rcp' for Recipes
                - 'shop' for Shopping
                - 'vid' for Video
            nlinks (int, optional): The number of links to retrieve.

        Returns:
            list: A unique set of URLs returned from the Google search.
        """
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
        """
        Generates a response from a GPT language model based on a specified prompt.
        
        Parameters:
            prompt (str): The prompt to send to the language model.
            openai_api_key (str): The API key for OpenAI, required for accessing the language model.
            generation_tk_limit (int, optional): The maximum number of tokens that the language model is allowed to generate.
            gpt_model (str, optional): The specific GPT model to use for generating responses.
            system_instruction (str, optional): Additional instructions to guide the language model's response.
        
        Returns:
            str: The response generated by the language model for the user query.
        """
        return get_gpt_response(
                user_prompt=prompt,
                openai_key=openai_api_key,
                generation_tk_limit=generation_tk_limit,
                preferred_model=gpt_model,
                system_instruction=system_instruction
            )
