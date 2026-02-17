import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

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


# Calculate MACD
def calculate_macd(df, fast=12, slow=26, signal=9):
    exp1 = df["Close"].ewm(span=fast, adjust=False).mean()
    exp2 = df["Close"].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    
    # Detect crossovers - use the histogram sign change for accuracy
    bullish_crossover = pd.Series(index=df.index, data=False)
    bearish_crossover = pd.Series(index=df.index, data=False)
    
    for i in range(1, len(histogram)):
        # Bullish: histogram changes from negative to positive
        if histogram.iloc[i-1] <= 0 and histogram.iloc[i] > 0:
            bullish_crossover.iloc[i] = True
        # Bearish: histogram changes from positive to negative
        elif histogram.iloc[i-1] >= 0 and histogram.iloc[i] < 0:
            bearish_crossover.iloc[i] = True
    
    return macd, signal_line, histogram, bullish_crossover, bearish_crossover

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
    title = f"ANGELONE {timeframe} Candlestick Chart with MACD"
    
    # Calculate MACD
    macd, signal_line, histogram, bullish_crossover, bearish_crossover = calculate_macd(df)
    
    # Create crossover scatter data for MACD panel
    bullish_points_macd = macd.copy()
    bullish_points_macd[~bullish_crossover] = float('nan')
    
    bearish_points_macd = macd.copy()
    bearish_points_macd[~bearish_crossover] = float('nan')
    
    # Create crossover scatter data for Price panel (at candle lows/highs)
    bullish_points_price = df["Low"].copy()
    bullish_points_price[~bullish_crossover] = float('nan')
    
    bearish_points_price = df["High"].copy()
    bearish_points_price[~bearish_crossover] = float('nan')
    
    # Create additional plots for MACD
    apds = [
        # Price panel markers (panel 0)
        mpf.make_addplot(bullish_points_price, panel=0, type="scatter", markersize=150, marker="^", color="green", alpha=0.6),
        mpf.make_addplot(bearish_points_price, panel=0, type="scatter", markersize=150, marker="v", color="red", alpha=0.6),
        # MACD panel
        mpf.make_addplot(macd, panel=2, color="blue", ylabel="MACD", label="MACD Line"),
        mpf.make_addplot(signal_line, panel=2, color="red", label="Signal Line"),
        mpf.make_addplot(histogram, panel=2, type="bar", color="gray", alpha=0.5, label="Histogram"),
        mpf.make_addplot(bullish_points_macd, panel=2, type="scatter", markersize=100, marker="^", color="green", alpha=0.6, label="Bullish Crossover"),
        mpf.make_addplot(bearish_points_macd, panel=2, type="scatter", markersize=100, marker="v", color="red", alpha=0.6, label="Bearish Crossover"),
    ]
    
    # Plot with returnfig to customize further
    fig, axes = mpf.plot(
        df,
        type="candle",
        style=style,
        title=title,
        ylabel="Price (INR)",
        volume=True,
        addplot=apds,
        figsize=(18, 10),
        returnfig=True,
    )
    
    # axes[0] = price panel, axes[2] = volume panel, axes[4] = MACD panel
    macd_ax = axes[4]
    
    # Add legend horizontally below the plot area
    macd_ax.legend(
        ["MACD Line (12,26)", "Signal Line (9)", "Histogram", "Bullish Crossover ▲", "Bearish Crossover ▼"],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.4),
        ncol=5,
        fontsize=11,
        frameon=True,
        fancybox=True,
        shadow=True,
    )
    
    # Add grid for better readability
    axes[0].grid(True, alpha=0.3, linestyle="--")
    macd_ax.grid(True, alpha=0.3, linestyle="--")
    
    # Add MACD zero line for reference
    macd_ax.axhline(0, color="black", linewidth=1, linestyle="--", alpha=0.5)
    
    plt.show()


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
