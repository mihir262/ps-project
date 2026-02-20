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


def simulate_trades(df, bullish, bearish):
    """Pair each bullish crossover with the next bearish crossover after it."""
    buy_dates = df.index[bullish.values]
    sell_dates = df.index[bearish.values]

    rows = []
    used = 0  # pointer into sell_dates
    for buy_date in buy_dates:
        while used < len(sell_dates) and sell_dates[used] <= buy_date:
            used += 1
        sell_date = sell_dates[used] if used < len(sell_dates) else df.index[-1]
        rows.append({"buy_date": buy_date,  "buy_price":  df.loc[buy_date,  "Close"],
                     "sell_date": sell_date, "sell_price": df.loc[sell_date, "Close"]})
        used += 1  # each sell can only be used once

    trades = pd.DataFrame(rows)
    if not trades.empty:
        trades["pnl"]     = trades["sell_price"] - trades["buy_price"]
        trades["pnl_pct"] = trades["pnl"] / trades["buy_price"] * 100
    return trades


def print_trade_summary(trades, timeframe):
    if trades.empty:
        print(f"\n{timeframe} — No trades generated")
        return

    display = pd.DataFrame({
        "Buy Date":  trades["buy_date"].dt.strftime("%Y-%m-%d"),
        "Buy ₹":     trades["buy_price"].round(2),
        "Sell Date": trades["sell_date"].dt.strftime("%Y-%m-%d"),
        "Sell ₹":    trades["sell_price"].round(2),
        "P&L ₹":     trades["pnl"].round(2).map("{:+.2f}".format),
        "%":         trades["pnl_pct"].round(2).map("{:+.2f}%".format),
        "":          trades["pnl"].map(lambda x: "✓" if x >= 0 else "✗"),
    })

    wins = (trades["pnl"] >= 0).sum()
    print(f"\n{timeframe} MACD Trade Log")
    print(display.to_string(index=False))
    print(f"\nTotal P&L: ₹{trades['pnl'].sum():+.2f} | Trades: {len(trades)} | "
          f"Wins: {wins} | Losses: {len(trades)-wins} | Win Rate: {wins/len(trades)*100:.1f}%\n")


def plot_candlestick(df, timeframe):
    macd, signal_line, histogram, bullish, bearish = calculate_macd(df)

    trades = simulate_trades(df, bullish, bearish)
    print_trade_summary(trades, timeframe)

    # Mark only the crossovers that produced actual trades
    buy_signals = pd.Series(index=df.index, data=float("nan"))
    sell_signals = pd.Series(index=df.index, data=float("nan"))
    if not trades.empty:
        buy_signals.loc[trades["buy_date"].values]   = df.loc[trades["buy_date"].values,  "Low"].values
        sell_signals.loc[trades["sell_date"].values] = df.loc[trades["sell_date"].values, "High"].values

    bull_macd = macd.where(bullish)
    bear_macd = macd.where(bearish)

    apds = [
        mpf.make_addplot(buy_signals, panel=0, type="scatter", markersize=120, marker="^", color=BULL_MARKER, alpha=0.9),
        mpf.make_addplot(sell_signals, panel=0, type="scatter", markersize=120, marker="v", color=BEAR_MARKER, alpha=0.9),
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

    total_pnl = trades["pnl"].sum() if not trades.empty else 0
    wins      = (trades["pnl"] >= 0).sum() if not trades.empty else 0
    pnl_str   = f"P&L: ₹{total_pnl:+,.2f}  |  {len(trades)} trades  |  {wins}W {len(trades)-wins}L"

    fig.suptitle(
        f"ANGELONE  ·  {timeframe}  ·  MACD (12, 26, 9)\n{pnl_str}",
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
        Line2D([0], [0], marker="^", color=BULL_MARKER, linestyle="None", markersize=8, label="Buy"),
        Line2D([0], [0], marker="v", color=BEAR_MARKER, linestyle="None", markersize=8, label="Sell"),
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
