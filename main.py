from scrapper import get_news_links, parse_webpage
from gpt_client import get_gpt_response, chunk

WATCHLIST = {
    "COMMODITIES": [
        "HG=F", # Copper
        "BZ=F", # Brent
        "CL=F", # Crude Oil
        "GC=F", # Gold
        "NG=F", # Natural Gas
        "SI=F", # Silver
        "CC=F" # Cocoa
    ],
    "FOREX": [
        "AUDCHF",
        'AUDJPY',
        'AUDUSD',
        "CADCHF",
        'CADJPY',
        'CHFJPY',
        'EURAUD',
        'EURCAD',
        'EURCHF',
        'EURGBP',
        'EURJPY',
        'EURUSD',
        "GBPAUD",
        "GBPJPY",
        'GBPUSD',
        "NZDCHF",
        "NZDJPY",
        'NZDUSD',
        'USDCAD',
        'USDCHF',
        'USDJPY'
    ]
}

for item in WATCHLIST["FOREX"]:
    links = get_news_links(item)
    news = ''
    for idx, link in enumerate(links, start=1):
        print(f"Parsing {link}...\n")
        news += f"""
        Article {idx}:
        "{parse_webpage(link)}"
        """

    news = chunk(news, 3000)
    print(f"Determining {item}...")
    res = get_gpt_response(
        user_prompt=f"""From these articles, determine if the sentiment for {item} is mainly bullish, bearish, or neutral:
        {news}
        
        Your response must strictly contain only one string ("bullish", "bearish", or "neutral").
        """
    )
    print(res)
    
    print("Article 1" in news)
    print("Article 2" in news)
    print("Article 3" in news)
    print("Article 4" in news)
    
    input("\n> ")