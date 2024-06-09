import pandas as pd
import os
from datetime import datetime, timedelta
from ta.trend import ADXIndicator, PSARIndicator
import yfinance as yf
import numpy as np
import json


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

EX_RATES = {
    'JPY': 0.0068,
    'USD': 1,
    'AUD': 0.66,
    'CAD': 0.75,
    'CHF': 1.17,
    'GBP': 1.27,
    "CNH": 7.19,
}


class CustomError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


def dump_df_to_csv(df, item_name, suffix=''):
    """Store a df into a local csv file.
    Default output filename will be <item_name>.csv.

    Args:
        df (DataFrame): df containing data for item_name
        item_name (str): Name of asset item
        suffix (str): If given, output filename will be <item_name>_<suffix>.csv [Default suffix='']

    Raises:
        CustomError: If file is not able to be created.
    """
    if suffix != '':
        suffix = '_' + suffix
    
    filename = f"{str(item_name)}{str(suffix)}.csv"    
    df.to_csv(filename)

    # Get the current working directory
    current_directory = os.getcwd()
    # Create the full path to the file
    file_path = os.path.join(current_directory, filename)
    # Check if the file exists
    
    if os.path.isfile(file_path):
        print(f"{filename} CREATED SUCCESSFULLY!")
    else:
        raise CustomError(f"ERROR while creating {filename}.")
    return


def get_date_ndays_apart(ndays, from_date=datetime.now()):
    """Given today's date or any other custom date, returns the date ndays ahead or earlier.

    Args:
        ndays (int): No. of days apart from today's date or from_date. 
        If negative input, then returns ndays earlier. 
        If positive input, then returns ndays ahead.
        from_date (datetime.datetime): Optional custom date to compute from. Default value is today's date.


    Returns:
        datetime.datetime: A datetime object of the date ndays apart.
    """
    if isinstance(from_date, str):
        from_date = datetime.strptime(from_date, "%Y-%m-%d %H:%M:%S")
    if not isinstance(from_date, datetime):
        raise CustomError("from_date is not a date-formatted string or datetime.datetime object.")
    return from_date + timedelta(days = ndays)


def attach_adx_clm(ohlc_df, period, clm_name="adx"):
    """Returns the input ohlc_df with a adx clm appended to it.
    [NOTE: sma of 2 has been applied to these adx values.]

    Args:
        ohlc_df (DataFrame): A df containing Open, High, Low, and Close series.
        period (int): Period to be used to compute adx.
        clm_name (str): Optional clm name for the newly created adx clm.

    Returns:
        DataFrame: the input df with the adx clm appended to it.
    """
    try:
        high, low, close = ohlc_df["High"], ohlc_df["Low"], ohlc_df["Close"]
    except:
        raise CustomError("No 'High', 'Low', or 'Close' clms found in input df.")
    
    try:
        adx_values = ADXIndicator(high, low, close, period, True)
        ohlc_df[clm_name] = adx_values.adx()
        ohlc_df[clm_name] = sma(ohlc_df[clm_name], 2)
    except:
        raise CustomError("Cannot create adx clm with suggested clm name.")

    return ohlc_df


def ema(ts, period):
    """Takes in a timeseries and returns a new series containing its ema values.

    Args:
        ts (Series): A timeseries of price values.
        period (int): Period to be used to compute ema.

    Returns:
        Series: A new timeseries containing ema values.
    """
    ema_series = ts.ewm(span=period, adjust=False).mean()
    return ema_series


def sma(ts, period):
    """Takes in a timeseries and returns a new series containing its sma values.

    Args:
        ts (Series): A timeseries of price values.
        period (int): Period to be used to compute sma.

    Returns:
        Series: A new timeseries containing sma values.
    """
    sma_series = ts.rolling(window=period).mean()
    return sma_series


def attach_psar_clm(ohlc_df):
    """Attaches a new row of parabolic sar values for a given ohlc_df.

    Args:
        ohlc_df (DataFrame): A df containing Open, High, Low, and Close timeseries.

    Returns:
        DataFrame: the input df with the psar clm appended to it.
    """
    try:
        high, low, close = ohlc_df["High"], ohlc_df["Low"], ohlc_df["Close"]
    except:
        raise CustomError("No 'High', 'Low', or 'Close' clms found in input df.")
    
    sar_indicator = PSARIndicator(high, low, close, 0.01, 0.2)
    ohlc_df["psar"] = sar_indicator.psar()
    return ohlc_df


def fetch_ohlc_data(item, interval, ticker="fx", *start_date):
    """Retrieve yfinance data and return as df, alongside a mean price clm which takes the mean of OHLC clms.

    Args:
        item (str): Basic ticker for yfinance
        interval (str): 5m,15m,30m,1h,1d,5d,1wk,1mo,3mo

    Returns:
        DataFrame: OHLC df with an appened mean price clm
    """
    # if start_date and start_date[0] > datetime.today():
    #     raise CustomError("Input start_date is in the future.")
    
    if interval not in ["5m","15m","30m","1h","1d","5d","1wk","1mo","3mo"]:
        raise CustomError("Unknown interval value.")
    
    if ticker == "fx":
        item = yf.Ticker(f"{item}=X")
    else:
        item = yf.Ticker(ticker)
    try:
        if not start_date:
          today = datetime.now()
          start_date = today + timedelta(days=-1000)
        else:
          start_date = start_date[0]
        
        data = item.history(interval=interval, start=start_date)
    except:
        raise CustomError("Invalid yfinance tinker id.")

    # Keep only required clms
    data = data[["Open", "High", "Low", "Close"]]

    # Create mean clm
    data['Mean'] = (data['High'] + data['Low'] + data['Close']) / 3

    # Make Date into a clm instead of index clm
    data.index.name = 'Date'
    data.reset_index(inplace=True)
    if interval not in ["5m","15m","30m","1h"]:
        data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%m/%d/%Y')
        data['Date'] = pd.to_datetime(data['Date'])

    return data


def keep_last_nrows(df, nrows):
    """Given a df, keep only the last nrows and reset their indexes to start from 0 accordingly.

    Args:
        df (DataFrame): Any df
        nrows (int): No of rows to keep

    Returns:
        DataFrame: A shorter df containing only the last nrows of original df.
    """
    if nrows <= 0:
        raise CustomError("Invalid nrows parameter.")
    
    try:
        return df.iloc[-1 * nrows:].reset_index(drop=True)
    except:
        raise CustomError("ERROR!")


def get_fib_levels(swing_high_price, swing_low_price):
    """Given a swing high and swing low price points, returns the Fibonacci retracement price levels in decreasing order.

    Args:
        swing_high_price (float): Swing high price value
        swing_low_price (float): Swing low price value

    Returns:
        list: A list containing the Fibonacci price points in decreasing order.
    """
    fibonacci_levels = [0.236, 0.382, 0.500, 0.618]
    price_range = swing_high_price - swing_low_price
    return [(swing_high_price - (level * price_range)) for level in fibonacci_levels]


def append_ema_signal(ohlc_df, ema1_name, ema1_period, ema2_name, ema2_period, signal_name):
    """Computes signal clm using ema criss-cross strategy on Open price points. Also appends the ema1 and ema2 clms.

    Args:
        ohlc_df (DataFrame): A df containing Open, High, Low, and Close series.
        ema1_name (str): clm name for the newly created ema1 clm.
        ema1_period (int): Period to be used to compute ema1.
        ema2_name (str): clm name for the newly created ema2 clm.
        ema2_period (int): Period to be used to compute ema2.
        signal_name (str): clm name for the newly created signal clm.

    Returns:
        DataFrame: Original ohlc_df with 3 new clms of ema1, ema2 and signal appended to it.
    """
    if ema1_period >= ema2_period:
        raise CustomError("ema1 period has to be lesser than ema2 period.")
    
    try:
        ohlc_df[ema1_name] = ema(ohlc_df["Open"], ema1_period)
        ohlc_df[ema2_name] = ema(ohlc_df["Open"], ema2_period)
    except:
        raise CustomError("No 'Open' clm found in input df.")
    
    ohlc_df[signal_name] = np.where(ohlc_df[ema1_name] <= ohlc_df[ema2_name], -1, 1)
    return ohlc_df


class Order:
    def __init__(self, item, start_price, signal, lots) -> None:
        self.item = item
        self.start_price = start_price
        self.signal = signal
        self.lots = lots

        if item in EX_RATES:
            self.rate = EX_RATES[item]
        else:
            self.rate = 1
            print("** Exchange rate for item not found. **\n")

        self.pips = 0
        self.profit = 0

    def close_order(self, end_price):
        if self.signal in [1, 2]:
            price_change = end_price - self.start_price
        elif self.signal in [-1, -2]:
            price_change = self.start_price - end_price
        else:
            return 0
        
        if self.item.endswith("JPY"):
            self.pips = price_change * 100
        else:
            self.pips = price_change * (10 ** 4)

        self.profit = price_change * 1000 * self.lots * self.rate
        return


def dump_to_txt_file(dic, filename):
    """Saves a dictionary data to a local file.

    Args:
        dic (dict): A dictionary containing data
        filename (str): Name of txt file.
    """
    # Get the current working directory
    current_directory = os.getcwd()
    # Create the full path to the file
    file_path = os.path.join(current_directory, filename)
    # Check if the file exists

    with open(file_path, 'w') as f:
        json.dump(dic, f, indent=4)
    return


def get_fractal(data, ranging_clm_name="isRanging"):
    """Get the fractal signal for the latest candlestick. The input ohlc df should have a column for isRanging.

    Args:
        data (DataFrame): OHLC df with an isRanging column preferably.
        ranging_clm_name (str, optional): Alternative name of the isRanging column if it is not "isRanging". Defaults to "isRanging".

    Returns:
        int: SwingLow/Long signal (1) or SwingHigh/short signal (-1) or 0 for no fractal signal detected.
    """
    if data[ranging_clm_name].iloc[-1] == 0:
        # SwingLow
        if data["Open"].iloc[-1] > data["Open"].iloc[-2]:
            if data["Open"].iloc[-2] < data["Open"].iloc[-3] and data["Low"].iloc[-2] < data["Low"].iloc[-3] and \
                data["Open"].iloc[-2] < data["Open"].iloc[-4] and data["Low"].iloc[-2] < data["Low"].iloc[-4] and \
                data["Open"].iloc[-2] < data["Open"].iloc[-5] and \
                data["Low"].iloc[-2] < data["Low"].iloc[-6]:
                return 1

        # SwingHigh
        if data["Open"].iloc[-1] < data["Open"].iloc[-2]:
            if data["Open"].iloc[-2] > data["Open"].iloc[-3] and data["High"].iloc[-2] > data["High"].iloc[-3] and \
                data["Open"].iloc[-2] > data["Open"].iloc[-4] and data["High"].iloc[-2] > data["High"].iloc[-4] and \
                data["Open"].iloc[-2] > data["Open"].iloc[-5] and \
                data["High"].iloc[-2] > data["High"].iloc[-6]:
                return -1

        # if data["nonranging_ema1"].iloc[i] >= data["nonranging_ema2"].iloc[i] and (data["nonranging_ema1"].iloc[i-1] <= data["nonranging_ema2"].iloc[i-1] or data["signal"].iloc[i-2] == -1):
        #     data.loc[i, "signal"] = 2
        # elif data["nonranging_ema1"].iloc[i] <= data["nonranging_ema2"].iloc[i] and (data["nonranging_ema1"].iloc[i-1] >= data["nonranging_ema2"].iloc[i-1] or data["signal"].iloc[i-2] == 1):
        #     data.loc[i, "signal"] = -2
        
        # if data["nonranging_ema1"].iloc[i] >= data["nonranging_ema2"].iloc[i] and (data["nonranging_ema1"].iloc[i-1] <= data["nonranging_ema2"].iloc[i-1]):
        #     data.loc[i, "signal"] = 2
        # elif data["nonranging_ema1"].iloc[i] <= data["nonranging_ema2"].iloc[i] and (data["nonranging_ema1"].iloc[i-1] >= data["nonranging_ema2"].iloc[i-1]):
        #     data.loc[i, "signal"] = -2

    else:
        assert(data[ranging_clm_name].iloc[-1] == 1)

        # If there was a signal in the past 2 candlesticks, then ignore current signal 
        # as there is a high chance it will be a repeat of that signal.
        if abs(data["signal"].iloc[-2]) != 1 and abs(data["signal"].iloc[-3]) != 1:
            # SwingLow
            if data["Open"].iloc[-2] < data["Open"].iloc[-3] and data["Low"].iloc[-2] < data["Low"].iloc[-3] and \
                data["Open"].iloc[-2] < data["Open"].iloc[-4] and data["Low"].iloc[-2] < data["Low"].iloc[-4] and \
                data["Open"].iloc[-2] < data["Open"].iloc[-5] and \
                data["Low"].iloc[-2] < data["Low"].iloc[-6] and \
                (data["Open"].iloc[-2] < data["Open"].iloc[-7] or data["Low"].iloc[-2] < data["Low"].iloc[-7]):
                return 1

            # SwingHigh
            elif data["Open"].iloc[-2] > data["Open"].iloc[-3] and data["High"].iloc[-2] > data["High"].iloc[-3] and \
                data["Open"].iloc[-2] > data["Open"].iloc[-4] and data["High"].iloc[-2] > data["High"].iloc[-4] and \
                data["Open"].iloc[-2] > data["Open"].iloc[-5] and \
                data["High"].iloc[-2] > data["High"].iloc[-6] and \
                (data["Open"].iloc[-2] > data["Open"].iloc[-7] or data["High"].iloc[-2] > data["High"].iloc[-7]): 
                return -1
        
    return 0
