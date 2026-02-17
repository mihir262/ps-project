import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

print("Loading data...")
daily_df = pd.read_csv("angelone_daily_365d.csv", header=[0, 1], index_col=0)
weekly_df = pd.read_csv("angelone_weekly_120w.csv", header=[0, 1], index_col=0)
monthly_df = pd.read_csv("angelone_monthly_60m.csv", header=[0, 1], index_col=0)


def clean_dataframe(df):
    df = df.iloc[1:]
    df.index = pd.to_datetime(df.index)
    df.columns = df.columns.droplevel(1)
    df.columns = df.columns.str.strip()
    df = df.astype(float)
    return df


daily_df = clean_dataframe(daily_df)
weekly_df = clean_dataframe(weekly_df)
monthly_df = clean_dataframe(monthly_df)

print(f"\n1. Daily: {len(daily_df)} records")
print(f"2. Weekly: {len(weekly_df)} records")
print(f"3. Monthly: {len(monthly_df)} records")


def calculate_macd(df, fast=12, slow=26, signal=9):
    exp1 = df["Close"].ewm(span=fast, adjust=False).mean()
    exp2 = df["Close"].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line

    bullish_crossover = pd.Series(index=df.index, data=False)
    bearish_crossover = pd.Series(index=df.index, data=False)

    for i in range(1, len(macd)):
        if macd.iloc[i-1] <= signal_line.iloc[i-1] and macd.iloc[i] > signal_line.iloc[i]:
            bullish_crossover.iloc[i-1] = True
        elif macd.iloc[i-1] >= signal_line.iloc[i-1] and macd.iloc[i] < signal_line.iloc[i]:
            bearish_crossover.iloc[i-1] = True

    return macd, signal_line, histogram, bullish_crossover, bearish_crossover


DARK_BG     = "#000000"
PANEL_BG    = "#0a0a0a"
GRID_COLOR  = "#222222"
TEXT_COLOR  = "#d4d4d4"
MACD_COLOR  = "#89b4fa"
SIGNAL_COLOR = "#f38ba8"
HIST_COLOR  = "#6c7086"
CANDLE_UP   = "#a6e3a1"
CANDLE_DOWN = "#f38ba8"
VOL_UP      = "#45475a"
VOL_DOWN    = "#585b70"
BULL_MARKER = "#f9e2af"
BEAR_MARKER = "#cba6f7"

style = mpf.make_mpf_style(
    base_mpf_style="nightclouds",
    marketcolors=mpf.make_marketcolors(
        up=CANDLE_UP, down=CANDLE_DOWN,
        edge={"up": CANDLE_UP, "down": CANDLE_DOWN},
        wick={"up": CANDLE_UP, "down": CANDLE_DOWN},
        volume={"up": VOL_UP, "down": VOL_DOWN},
    ),
    facecolor=PANEL_BG,
    figcolor=DARK_BG,
    gridcolor=GRID_COLOR,
    gridstyle="--",
    rc={
        "font.size": 11, "axes.labelsize": 12, "axes.titlesize": 16,
        "xtick.labelsize": 10, "ytick.labelsize": 10,
        "axes.edgecolor": GRID_COLOR, "axes.linewidth": 1,
        "axes.labelcolor": TEXT_COLOR,
        "xtick.color": TEXT_COLOR, "ytick.color": TEXT_COLOR,
        "text.color": TEXT_COLOR,
    },
)


def plot_candlestick(df, timeframe):
    macd, signal_line, histogram, bullish, bearish = calculate_macd(df)

    bull_macd = macd.where(bullish)
    bear_macd = macd.where(bearish)
    bull_price = df["Low"].where(bullish)
    bear_price = df["High"].where(bearish)

    apds = [
        mpf.make_addplot(bull_price, panel=0, type="scatter", markersize=120, marker="^", color=BULL_MARKER, alpha=0.9),
        mpf.make_addplot(bear_price, panel=0, type="scatter", markersize=120, marker="v", color=BEAR_MARKER, alpha=0.9),
        mpf.make_addplot(macd, panel=2, color=MACD_COLOR, width=1.5, ylabel="MACD"),
        mpf.make_addplot(signal_line, panel=2, color=SIGNAL_COLOR, width=1.5),
        mpf.make_addplot(histogram, panel=2, type="bar", color=HIST_COLOR, alpha=0.4),
        mpf.make_addplot(bull_macd, panel=2, type="scatter", markersize=80, marker="^", color=BULL_MARKER, alpha=0.9),
        mpf.make_addplot(bear_macd, panel=2, type="scatter", markersize=80, marker="v", color=BEAR_MARKER, alpha=0.9),
    ]

    fig, axes = mpf.plot(
        df, type="candle", style=style, ylabel="Price (₹)",
        volume=True, addplot=apds, figsize=(20, 11),
        returnfig=True, panel_ratios=(4, 1, 2), tight_layout=True,
    )

    fig.suptitle(
        f"ANGELONE  ·  {timeframe}  ·  MACD (12, 26, 9)",
        fontsize=16, fontweight="bold", color=TEXT_COLOR, y=0.98,
    )

    price_ax, vol_ax, macd_ax = axes[0], axes[2], axes[4]
    price_ax.set_ylabel("Price (₹)", fontsize=11, color=TEXT_COLOR)
    vol_ax.set_ylabel("Vol", fontsize=10, color=TEXT_COLOR)
    macd_ax.set_ylabel("MACD", fontsize=10, color=TEXT_COLOR)
    macd_ax.axhline(0, color=GRID_COLOR, linewidth=1, linestyle="-", alpha=0.6)

    for ax in [price_ax, macd_ax]:
        ax.grid(True, alpha=0.15, linestyle="--", color=GRID_COLOR)

    legend_items = [
        Line2D([0], [0], color=MACD_COLOR, linewidth=2, label="MACD"),
        Line2D([0], [0], color=SIGNAL_COLOR, linewidth=2, label="Signal"),
        Line2D([0], [0], color=HIST_COLOR, linewidth=6, alpha=0.4, label="Histogram"),
        Line2D([0], [0], marker="^", color=BULL_MARKER, linestyle="None", markersize=8, label="Bullish ✕"),
        Line2D([0], [0], marker="v", color=BEAR_MARKER, linestyle="None", markersize=8, label="Bearish ✕"),
    ]
    macd_ax.legend(
        handles=legend_items, loc="lower left",
        fontsize=9, frameon=True, facecolor=DARK_BG, edgecolor=GRID_COLOR,
        labelcolor=TEXT_COLOR, ncol=5, columnspacing=1.5,
    )

    plt.subplots_adjust(hspace=0.05)
    plt.show()


print("\nSelect timeframe to plot:")
print("1. Daily (365 days)")
print("2. Weekly (120 weeks)")
print("3. Monthly (60 months)")
print("4. All three")

choice = input("\nEnter your choice (1-4): ").strip()

if choice == "1":
    plot_candlestick(daily_df, "Daily")
elif choice == "2":
    plot_candlestick(weekly_df, "Weekly")
elif choice == "3":
    plot_candlestick(monthly_df, "Monthly")
elif choice == "4":
    for df, tf in [(daily_df, "Daily"), (weekly_df, "Weekly"), (monthly_df, "Monthly")]:
        plot_candlestick(df, tf)
else:
    print("Invalid choice!")
