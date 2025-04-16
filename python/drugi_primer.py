import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

df = pd.read_csv("../podatki/parking_data.csv")
df = df[(df["Prosto"] != "/") & (~df["Prosto"].isna()) & (df["Location"] != "Slovenčeva ulica")]

# Ensure datetime and int types are set
df["Datum"] = pd.to_datetime(df["Datum"])
df["Prosto"] = df["Prosto"].astype(int)

# Group by time and sum 'Prosto' (free spots) across all locations
grouped = df.groupby("Datum").agg({"Prosto": "sum"}).reset_index()

# Optional: Smooth the line a bit
grouped["Smoothed"] = grouped["Prosto"].rolling(window=4, min_periods=1).mean()

# Plotting
plt.figure(figsize=(15, 5))
plt.plot(grouped["Datum"], grouped["Smoothed"], color="green", linewidth=2, label="Skupno število prostih mest")

# Make X-axis more detailed
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=24))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
plt.grid(axis='x', linestyle='--', color='gray', alpha=0.5)


# Get tick positions and convert to datetime using mdates
xticks = plt.gca().get_xticks()
tick_dates = [mdates.num2date(tick) for tick in xticks]

# Loop through each pair of ticks
for i in range(len(tick_dates) - 1):
    mid = tick_dates[i] + (tick_dates[i+1] - tick_dates[i]) / 2
    if mid.weekday() in [6]:  # 5 = Saturday, 6 = Sunday
        plt.axvspan(tick_dates[i], tick_dates[i+2], color='lightblue', alpha=1, zorder=0)


plt.xlabel("Čas")
plt.ylabel("Število prostih mest")
plt.title("Skupno število prostih parkirnih mest skozi čas")
plt.legend(loc="lower left")
plt.tight_layout()
plt.show()


y = 0