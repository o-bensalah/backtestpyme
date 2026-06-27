import io
import urllib.request
import pandas as pd
import yfinance as yf
import sys
from datetime import datetime

end_date = datetime.strptime("2026-06-01", "%Y-%m-%d")
start_date = end_date.replace(year=end_date.year - 3)

USAGE = (
    "Usage: python dataCollector.py <option>\n"
    "  1  S&P 500 (fresh from Wikipedia)\n"
    "  2  T-Bill (^IRX)\n"
    "  3  Russell 3000 (iShares IWV holdings)\n"
    "  4  SPY\n"
)

def get_sp500_tickers_wiki():
    sp500 = pd.read_html(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        storage_options={"User-Agent": "Mozilla/5.0"}
    )[0]
    sp500 = sp500.drop_duplicates(subset="CIK")
    return [t.replace(".", "-") for t in sp500["Symbol"].tolist()]

def get_russell3000_tickers_ishares():
    url = (
        "https://www.blackrock.com/varnish-api/blk-one01-product-data/product-data/api/v1/"
        "get-fund-document?appType=PRODUCT_PAGE&appSubType=ISHARES&targetSite=us-ishares"
        "&locale=en_US&portfolioId=239714&userType=individual&component=holdings"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        text = response.read().decode("utf-8")

    lines = text.splitlines()
    header_idx = next(i for i, line in enumerate(lines) if line.startswith("Ticker"))
    df = pd.read_csv(io.StringIO("\n".join(lines[header_idx:])), dtype=str)
    tickers = df[df["Asset Class"] == "Equity"]["Ticker"].dropna()
    return [t.replace(".", "-") for t in tickers.tolist()]

def download(tickers, filename):
    data = yf.download(tickers, start_date, end_date)["Close"]
    data.to_csv(f"data/{filename}")


if len(sys.argv) < 2:
    print(USAGE)
    sys.exit(1)

match sys.argv[1]:
    case "1":
        download(get_sp500_tickers_wiki(), "sp500_data.csv")
    case "2":
        download("^IRX", "tbill_data.csv")
    case "3":
        download(get_russell3000_tickers_ishares(), "russel3000_data.csv")
    case "4":
        download("SPY", "spy_data.csv")
    case _:
        print(USAGE)
        sys.exit(1)