import os
import random
import time
import ssl
from http.cookiejar import LWPCookieJar
from urllib.request import Request, urlopen
from urllib.parse import quote_plus, urlparse, parse_qs
from bs4 import BeautifulSoup
from datetime import datetime, date

# Define URL templates
URL_HOME = "https://www.google.%(tld)s/"
URL_SEARCH = "https://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&" \
             "btnG=Google+Search&tbs=%(tbs)s&safe=%(safe)s&" \
             "cr=%(country)s&tbm=%(tbm)s"
URL_NEXT_PAGE = "https://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&" \
                "start=%(start)d&tbs=%(tbs)s&safe=%(safe)s&" \
                "cr=%(country)s&tbm=%(tbm)s"
URL_NEXT_PAGE_NUM = "https://www.google.%(tld)s/search?hl=%(lang)s&" \
                    "q=%(query)s&num=%(num)d&start=%(start)d&tbs=%(tbs)s&" \
                    "safe=%(safe)s&cr=%(country)s&tbm=%(tbm)s"

# List of common/famous and latest user agents
USER_AGENTS_LIST = [
    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    # Firefox
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
    # Safari
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    # Edge
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.49',
    # Opera
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 OPR/76.0.4017.123'
]
home_folder = os.getenv('HOME', os.getenv('USERHOME', '.'))
cookie_jar = LWPCookieJar(os.path.join(home_folder, '.google-cookie'))
try:
    cookie_jar.load()
except Exception:
    pass


def get_random_user_agent():
    """Return a random user agent string."""
    return random.choice(USER_AGENTS_LIST)


def get_tbs(preferred_date):
    """Format the tbs parameter for Google search."""
    preferred_date = to_date(preferred_date)
    if is_future_date(preferred_date):
        raise ValueError(f"Cannot be a future date.")
    return 'cdr:1,cd_min:{},cd_max:{}'.format(
        preferred_date.strftime('%m/%d/%Y'), preferred_date.strftime('%m/%d/%Y')
    )


def to_date(input_date):
    """
    Convert a datetime.datetime object or a string containing a date
    into a datetime.date object.

    :param input_date: A datetime.datetime object or a string representing a date.
    :param date_format: A string representing the expected format of the date string (optional).
    :return: A datetime.date object.
    """
    if isinstance(input_date, datetime):
        return input_date.date()
    elif isinstance(input_date, str):
        try:
            return datetime.strptime(input_date, '%m/%d/%Y').date()
        except ValueError:
            raise ValueError(f"Date string does not match format '%m/%d/%Y'")
    else:
        raise TypeError("Input must be a datetime.datetime object or a string")


def is_future_date(input_date):
    """
    Check if a given datetime.date object is a date in the future.

    :param input_date: A datetime.date object.
    :return: True if the input_date is in the future, False otherwise.
    """
    if not isinstance(input_date, date) and not isinstance(input_date, datetime):
        raise TypeError("Input date must be a datetime.date object")
    
    today = date.today()
    print(today, input_date)
    return input_date > today


def get_page(url, user_agent=None, verify_ssl=True):
    """Request the given URL and return the response page."""
    if user_agent is None:
        user_agent = get_random_user_agent()
    request = Request(url, headers={'User-Agent': user_agent})
    cookie_jar.add_cookie_header(request)
    if verify_ssl:
        response = urlopen(request)
    else:
        context = ssl._create_unverified_context()
        response = urlopen(request, context=context)
    cookie_jar.extract_cookies(response, request)
    html = response.read()
    response.close()
    try:
        cookie_jar.save()
    except Exception:
        pass
    return html

def filter_result(link):
    """Filter valid links from Google search results."""
    if link.startswith('/url?'):
        link = parse_qs(urlparse(link).query)['q'][0]
    o = urlparse(link)
    if o.netloc and 'google' not in o.netloc:
        return link

def search_google(query, tld='com', lang='en', tbs='0', safe='off', num=10, start=0,
                  stop=None, pause=2.0, country='', tbm='', extra_params=None,
                  user_agent=None, verify_ssl=True):
    """Search the given query string using Google."""
    query = quote_plus(query)
    extra_params = extra_params or {}
    
    # Check for overlapping extra parameters
    for param in ['hl', 'q', 'num', 'btnG', 'start', 'tbs', 'safe', 'cr', 'tbm']:
        if param in extra_params:
            raise ValueError(f'GET parameter "{param}" is overlapping with the built-in GET parameter')

    # Get initial page to set cookies
    get_page(URL_HOME % vars(), user_agent, verify_ssl)
    
    # Build the search URL
    url = URL_SEARCH if start == 0 else URL_NEXT_PAGE
    url = url % vars()

    # Search results
    results = set()
    count = 0

    while not stop or count < stop:
        # Append extra parameters
        for k, v in extra_params.items():
            url += f'&{quote_plus(k)}={quote_plus(v)}'
        
        # Wait between requests to avoid being banned
        time.sleep(pause)
        
        # Get the search results page
        html = get_page(url, user_agent, verify_ssl)
        soup = BeautifulSoup(html, 'html.parser')
        anchors = soup.find(id='search').find_all('a') if soup.find(id='search') else soup.find_all('a')

        for a in anchors:
            link = a.get('href')
            if link:
                link = filter_result(link)
                if link and link not in results:
                    results.add(link)
                    yield link
                    count += 1
                    if stop and count >= stop:
                        return
        
        if count == len(results):
            break
        
        start += num
        url = URL_NEXT_PAGE % vars() if num == 10 else URL_NEXT_PAGE_NUM % vars()


def lucky(*args, **kwargs):
    """Shortcut to single-item search. Returns the first found URL."""
    return next(search_google(*args, **kwargs))


# Example usage
# if __name__ == "__main__":
#     for url in search_google('EURUSD analysis', stop=4, pause=1, tbm="nws", tbs=get_tbs("06/06/2024")):
#         print(url)