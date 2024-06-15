import os
import time
import ssl
from http.cookiejar import LWPCookieJar
from urllib.request import Request, urlopen
from urllib.parse import quote_plus, urlparse, parse_qs
from bs4 import BeautifulSoup
from datetime import datetime, date
import utils

# Initialize cookie jar at script directory
current_folder = os.path.dirname(os.path.abspath(__file__))
cookie_jar_path = os.path.join(current_folder, '.google-cookie')
cookie_jar = LWPCookieJar(cookie_jar_path)
try:
    cookie_jar.load()
except Exception:
    pass  # Handle exceptions or log errors as needed


def get_tbs(preferred_date):
    """Format the tbs parameter for Google search."""
    
    if preferred_date == '0':
        return '0'
        
    preferred_date = to_date(preferred_date)
    if is_future_date(preferred_date):
        raise ValueError(f"Cannot be a future date.")
    date_str = preferred_date.strftime('%m/%d/%Y')
    return f"cdr:1,cd_min:{date_str},cd_max:{date_str}"


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
    return input_date > today


def get_page(url, user_agent=None, verify_ssl=True):
    """Retrieve a webpage with optional SSL verification."""
    if user_agent is None:
        user_agent = utils.get_random_user_agent()
    request = Request(url, headers={'User-Agent': user_agent})
    cookie_jar.add_cookie_header(request)
    
    context = ssl.create_default_context() if verify_ssl else ssl._create_unverified_context()
    response = urlopen(request, context=context)
    cookie_jar.extract_cookies(response, request)
    html_content = response.read()
    response.close()
    
    try:
        cookie_jar.save()
    except Exception:
        pass
    
    return html_content


def filter_result(link):
    """Filter valid links from Google search results."""
    if link.startswith('/url?'):
        link = parse_qs(urlparse(link).query)['q'][0]
    o = urlparse(link)
    if o.netloc and 'google' not in o.netloc:
        return link


def search_google(query, tld='com', lang='en', tbs='0', safe='off',
                  stop=None, pause=1.0, country='', tbm='', user_agent=None):
    """Perform a Google search and yield found URLs."""
    query = quote_plus(query)
    initial_url = utils.GOOGLE_HOMEPAGE_URL % vars()
    get_page(initial_url, user_agent)

    results = set()
    count = 0

    while not stop or count < stop:
        time.sleep(pause)  # Pause to avoid rate limiting
        search_url = utils.GOOGLE_SEARCH_RESULTS_URL % vars()
        html = get_page(search_url, user_agent)
        soup = BeautifulSoup(html, 'html.parser')
        anchors = soup.find(id='search').find_all('a') if soup.find(id='search') else soup.find_all('a')

        for anchor in anchors:
            link = anchor.get('href')
            if link and (filtered_link := filter_result(link)) and filtered_link not in results:
                results.add(filtered_link)
                yield filtered_link
                count += 1
                if stop and count >= stop:
                    break
        
        if count == len(results):
            break


# Example usage
if __name__ == "__main__":
    for url in search_google('EURUSD analysis', stop=4, pause=1, tbm="nws", tbs=get_tbs("06/06/2023")):
        print(url)