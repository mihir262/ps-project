import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

symbol = "ANGELONE.NS"
end_date = datetime.now()

# 1. Fetch 365 days of daily data
start_date_daily = end_date - timedelta(days=365)

print(f"Fetching daily data from {start_date_daily.date()} to {end_date.date()}...")
daily_data = yf.download(
    symbol, start=start_date_daily, end=end_date, interval="1d", progress=False
)
daily_data.to_csv("angelone_daily_365d.csv")

print(f"Daily data: {len(daily_data)} records saved to 'angelone_daily_365d.csv'")
print(daily_data.tail())

# 2. Fetch 120 weeks of weekly data
start_date_weekly = end_date - timedelta(weeks=120)

print(f"\nFetching weekly data from {start_date_weekly.date()} to {end_date.date()}...")

weekly_data = yf.download(
    symbol, start=start_date_weekly, end=end_date, interval="1wk", progress=False
)
weekly_data.to_csv("angelone_weekly_120w.csv")

print(f"Weekly data: {len(weekly_data)} records saved to 'angelone_weekly_120w.csv'")
print(weekly_data.tail())

# 3. Fetch 60 months of monthly data
start_date_monthly = end_date - timedelta(days=60 * 30)

print(
    f"\nFetching m onthly data from {start_date_monthly.date()} to {end_date.date()}..."
)
monthly_data = yf.download(
    symbol, start=start_date_monthly, end=end_date, interval="1mo", progress=False
)
monthly_data.to_csv("angelone_monthly_60m.csv")

print(f"Monthly data: {len(monthly_data)} records saved to 'angelone_monthly_60m.csv'")
print(monthly_data.tail())
