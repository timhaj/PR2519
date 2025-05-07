import pandas as pd
import matplotlib.pyplot as plt
import datetime

df = pd.read_csv("./podatki/parking_data.csv")
df2 = pd.read_csv("./podatki/parking_data2.csv")
df = pd.concat([df, df2])
df = df[(df["Prosto"] != "/") & (~df["Prosto"].isna()) & (df["Location"] != "Slovenčeva ulica")]

base_date = pd.to_datetime("1970-01-01")
p = df[df["Location"] == "Gospodarsko razstavišče"].copy()
p["Datum"] = pd.to_datetime(p["Datum"])
plt.figure(figsize=(15, 5))

all_days_data = []
for day in pd.date_range(start="2025-03-18", end="2025-04-15"):
    day_data = p[(p["Datum"] >= day) & (p["Datum"] < day + pd.Timedelta(days=1))].copy()

    if str(day) in ["2025-03-29 00:00:00", "2025-04-05 00:00:00", "2025-04-07 00:00:00", "2025-04-08 00:00:00", "2025-04-09 00:00:00"]:
        continue

    # If exactly 95 rows, duplicate the last one
    #print(f"Day: {day}:{len(day_data)}")
    # if len(day_data) == 95:
    #     day_data = pd.concat([day_data, day_data.tail(1)], ignore_index=True)

    day_data["Time"] = base_date + (day_data["Datum"].dt.hour * pd.Timedelta(hours=1)) + (
                day_data["Datum"].dt.minute * pd.Timedelta(minutes=1))
    day_data["Normalized"] = 100 - (day_data["Prosto"].astype(int) / day_data["Na voljo"].astype(int) * 100)
    all_days_data.append(day_data[["Time", "Normalized"]])
    plt.plot(day_data["Time"], day_data["Normalized"], label=day.strftime("%Y-%m-%d"))


combined = pd.concat(all_days_data)
combined['To15min'] = combined['Time'].dt.round('15min').dt.time.apply(lambda t: datetime.datetime.combine(datetime.datetime(1970, 1, 1), t))
combined = combined[["To15min", "Normalized"]]
avg_data = combined.groupby("To15min").mean().reset_index()
#avg_data = combined.groupby("Time").mean().reset_index()
#avg_data["Smoothed"] = avg_data["Normalized"].rolling(window=10, min_periods=1).mean()
plt.plot(avg_data["To15min"], avg_data["Normalized"], color="black", linewidth=3, label="Povprečje")
plt.ylim(-50, 105)
tick_locs = pd.date_range(start=base_date, periods=25, freq="1H")
tick_labels = tick_locs.strftime('%H:%M')
plt.xticks(ticks=tick_locs, labels=tick_labels)
plt.margins(0)
plt.xlabel("Čas")
plt.ylabel("% zasedenosti")
plt.title('Dnevna primerjava zasedenosti parkirišča "PH Kongresni trg" (24h)')
plt.legend(ncol=3, fontsize=8)
plt.tight_layout()
plt.show()