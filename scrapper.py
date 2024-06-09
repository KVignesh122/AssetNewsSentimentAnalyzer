from bs4 import BeautifulSoup
import requests
from readability import Document
from websearch import search_google, get_tbs
import random
import aiohttp
import asyncio

# REQUEST_SUCCESS = 200


# def parse_webpage(url_link):
#     try:
#         response = requests.get(url_link)
#         if response.status_code == REQUEST_SUCCESS:
#             doc = Document(response.content)
#             soup = BeautifulSoup(doc.summary(), 'html.parser')
#             return soup.get_text(strip=True)
#         return ''
#     except Exception as e:
#         print(f"Error: {e}")
#         return ''

# List of user agents for requests
USER_AGENTS_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.49',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 OPR/76.0.4017.123'
]

async def fetch(session, url):
    headers = {'User-Agent': random.choice(USER_AGENTS_LIST)}
    try:
        timeout = aiohttp.ClientTimeout(total=60)  # Increasing the total timeout to 60 seconds
        await asyncio.sleep(0.5)
        async with session.get(url, headers=headers, timeout=timeout) as response:
            return await response.text()
    except aiohttp.ClientError as e:
        print(f"Client error: {e}")
        return None
    except asyncio.TimeoutError:
        print("The request timed out")
        return None

async def parse_webpage(url_link):
    async with aiohttp.ClientSession() as session:
        html_content = await fetch(session, url_link)
        if html_content is not None:
            doc = Document(html_content)
            soup = BeautifulSoup(doc.summary(), 'html.parser')
            return soup.get_text(strip=True)
        return ''


def get_news_links(asset_name: str, date=None) -> list:
    links = []
    
    additional_queries = [
        asset_name + " technical analysis",
        asset_name + " price sentiment",
        asset_name + " trading signal",
        asset_name,
    ]
    i = 0
    
    print("Entering search")
    while len(links) < 4 and i <= 3:
        if date:
            links += list(search_google(additional_queries[i], stop=4, pause=0.5, tbm="nws", tbs=get_tbs(date)))
        else:
            links += list(search_google(additional_queries[i], stop=4, pause=0.5, tbm="nws"))
        links = list(set(links))
        i += 1
    print("Exiting search")
    
    return links
