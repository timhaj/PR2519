import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

df = pd.read_csv("./parking_data.csv")
df = df[(df["Prosto"] != "/") & (~df["Prosto"].isna())]





# Base date to normalize time (for 24h overlay)
base_date = pd.to_datetime("1970-01-01")

# Filter location and convert 'Datum' to datetime
p = df[df["Location"] == "PH Kongresni trg"].copy()
p["Datum"] = pd.to_datetime(p["Datum"])


day = p[(p["Datum"] > "2025-03-28") & (p["Datum"] < "2025-03-29")]
day2 = p[(p["Datum"] > "2025-03-29") & (p["Datum"] < "2025-03-30")]

# Create a figure
plt.figure(figsize=(15, 5))

# Loop over each day
for day in pd.date_range(start="2025-03-18", end="2025-03-29"):
    # Slice data for a single day
    day_data = p[(p["Datum"] >= day) & (p["Datum"] < day + pd.Timedelta(days=1))].copy()

    if day_data.empty:
        continue  # skip if no data

    # If exactly 95 rows, duplicate the last one
    if len(day_data) == 95:
        day_data = pd.concat([day_data, day_data.tail(1)], ignore_index=True)

    # Normalize time to same day (e.g., 1970-01-01 HH:MM)
    day_data["Time"] = base_date + (day_data["Datum"].dt.hour * pd.Timedelta(hours=1)) + (
                day_data["Datum"].dt.minute * pd.Timedelta(minutes=1))

    # Calculate normalized occupancy
    day_data["Normalized"] = 100 - (day_data["Prosto"].astype(int) / day_data["Na voljo"].astype(int) * 100)

    # Plot
    plt.plot(day_data["Time"], day_data["Normalized"], label=day.strftime("%Y-%m-%d"))

# Y-axis
plt.ylim(0, 105)

# X-axis ticks every hour
tick_locs = pd.date_range(start=base_date, periods=25, freq="1H")
tick_labels = tick_locs.strftime('%H:%M')
plt.xticks(ticks=tick_locs, labels=tick_labels)

plt.margins(0)
plt.xlabel("Čas (HH:MM)")
plt.ylabel("% zasedenosti")
plt.title('Dnevna primerjava zasedenosti parkirišča "PH Kongresni trg" (24h)')
plt.legend(ncol=3, fontsize=8)  # Adjust layout if there are many days
plt.tight_layout()
plt.show()

y = 0

