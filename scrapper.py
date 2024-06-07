from bs4 import BeautifulSoup
import requests
from readability import Document
from websearch import search_google, get_tbs

REQUEST_SUCCESS = 200


def parse_webpage(url_link):
    try:
        response = requests.get(url_link)
        if response.status_code == REQUEST_SUCCESS:
            doc = Document(response.content)
            soup = BeautifulSoup(doc.summary(), 'html.parser')
            return soup.get_text(strip=True)
        return ''
    except Exception as e:
        print(f"Error: {e}")
        return ''


def get_news_links(query: str, date=None) -> list:
    links = []
    if date:
        links += list(search_google(query, stop=4, pause=2, tbm="nws", tbs=get_tbs(date)))
    else:
        links += list(search_google(query, stop=4, pause=2, tbm="nws"))
    links = list(set(links))
    return links
