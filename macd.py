import mplfinance as mpf
import pandas as pd

# Load data
print("Loading data...")
daily_df = pd.read_csv("angelone_daily_365d.csv", header=[0, 1], index_col=0)
weekly_df = pd.read_csv("angelone_weekly_120w.csv", header=[0, 1], index_col=0)
monthly_df = pd.read_csv("angelone_monthly_60m.csv", header=[0, 1], index_col=0)


# Clean up the dataframes - remove the ticker row and convert to proper format
def clean_dataframe(df):
    df = df.iloc[1:]  # Remove ticker row
    df.index = pd.to_datetime(df.index)
    df.columns = df.columns.droplevel(1)  # Remove ticker level from columns
    df.columns = df.columns.str.strip()  # Remove leading/trailing whitespace
    df = df.astype(float)
    return df


daily_df = clean_dataframe(daily_df)
weekly_df = clean_dataframe(weekly_df)
monthly_df = clean_dataframe(monthly_df)

print("\nLoaded data:")
print(f"1. Daily data: {len(daily_df)} records")
print(f"2. Weekly data: {len(weekly_df)} records")
print(f"3. Monthly data: {len(monthly_df)} records")

# Enhanced style for projector visibility
style = mpf.make_mpf_style(
    base_mpf_style="charles",
    rc={
        "font.size": 14,
        "axes.labelsize": 16,
        "axes.titlesize": 20,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
        "figure.facecolor": "white",
        "axes.edgecolor": "black",
        "axes.linewidth": 2,
        "figure.autolayout": True,
    },
)


# Plotting function
def plot_candlestick(df, timeframe):
    title = f"ANGELONE {timeframe} Candlestick Chart"
    mpf.plot(
        df,
        type="candle",
        style=style,
        title=title,
        ylabel="Price (INR)",
        volume=True,
        figsize=(18, 10),
    )


# Menu to choose timeframe
print("\nSelect timeframe to plot:")
print("1. Daily (365 days)")
print("2. Weekly (120 weeks)")
print("3. Monthly (60 months)")
print("4. All three")

choice = input("\nEnter your choice (1-4): ").strip()

if choice == "1":
    print("\nPlotting daily chart...")
    plot_candlestick(daily_df, "Daily")
elif choice == "2":
    print("\nPlotting weekly chart...")
    plot_candlestick(weekly_df, "Weekly")
elif choice == "3":
    print("\nPlotting monthly chart...")
    plot_candlestick(monthly_df, "Monthly")
elif choice == "4":
    print("\nPlotting all charts...")
    plot_candlestick(daily_df, "Daily")
    plot_candlestick(weekly_df, "Weekly")
    plot_candlestick(monthly_df, "Monthly")
else:
    print("Invalid choice!")

print("\nDone!")
