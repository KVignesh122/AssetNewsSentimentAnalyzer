from bs4 import BeautifulSoup
from readability import Document
from websearch_funcs import search_google, get_tbs
import aiohttp
import asyncio
from utils import get_random_user_agent


async def fetch(session, url):
    headers = {'User-Agent': get_random_user_agent()}
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
