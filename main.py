from scrapper import get_news_links, parse_webpage
from gpt_client import get_gpt_response, chunk
from sbc import get_date_ndays_apart, fetch_ohlc_data
import numpy as np
import asyncio

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

start_date = get_date_ndays_apart(-70)
df = fetch_ohlc_data('USDJPY', "1d", "fx", start_date)
# print(df)
# print(len(df))


async def get_sentiment(item, date=None):
    links = get_news_links(item, date=date)
    assert(len(links) <= 4)
    
    news = ''
    for idx, link in enumerate(links, start=1):
        # print(f"Parsing {link}...\n")
        news += f"""
            Article {idx}:
            "{await parse_webpage(link)}"
            """

    news = chunk(news, 3200)
    print(f"Determining {item}...")
    res = get_gpt_response(
            user_prompt=f"""Based on all your knowlege of financial markets and textual analysis, 
            assess information from all these articles and determine if the sentiment for {item} is mainly bullish, bearish, or neutral:
            {news}
            Your response must strictly contain only one word string ("bullish", "bearish", or "neutral") and no other words.
            """
        )
    print(res)
    return res


async def create_csv():
    df["Sentiment"] = np.nan
    for i in range(len(df)):
        sent_text = await get_sentiment('USDJPY', df["Date"].iloc[i])
        if "neutral" in sent_text.lower():
            df.at[i, "Sentiment"] = 0
        elif "bullish" in sent_text.lower():
            df.at[i, "Sentiment"] = 1
        else:
            try:
                assert("bearish" in sent_text.lower())
                df.at[i, "Sentiment"] = -1
            except:
                print(sent_text)
        assert(df["Sentiment"].iloc[i] in [-1, 0, 1])

    df.to_csv("sentiments.csv")

asyncio.run(create_csv())