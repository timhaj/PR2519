import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

days = ["pon", "tor", "sre", "čet", "pet", "sob", "ned"]
df = pd.read_csv("../podatki/parking_data.csv")
df = df[(df["Prosto"] != "/") & (~df["Prosto"].isna())]
df["Prosto"] = pd.to_numeric(df["Prosto"])
df["Na voljo"] = pd.to_numeric(df["Na voljo"])
df["Zasedenost"] = (1 -(df["Prosto"]  / df["Na voljo"])) * 100
df["Datum"] = pd.to_datetime(df["Datum"])
#print(df["Datum"].weekday)
df["Datum"] = df["Datum"].dt.day_of_week
#df["Datum"] = df["Datum"].weekday
mask = df['Zasedenost'] < 0
df.loc[mask, 'Zasedenost'] = 0
short = df[["Datum", "Prosto", "Na voljo", "Zasedenost"]]
zasedenost = short.groupby("Datum").agg("mean")
a = zasedenost.iloc[:, 2].to_list()
print(a)

print(zasedenost)


plt.bar(days, a)
plt.title("Porazdelitev zasedenosti skozi teden")
plt.xlabel("Dan v tednu")
plt.ylabel("Povprečna zasedenost parkirišča [%]")
plt.show()