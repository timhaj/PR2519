import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

cene = {
"Sanatorij Emona" : 1.20,
"Metelkova ulica" : 1.20,
"Krekov trg" : 1.20,

"Bežigrad" : 0.70,
"Gospodarsko razstavišče" : 0.70,
"Mirje" : 0.70,
"Trg mladinskih delovnih brigad" : 0.70,
"Tivoli I." : 0.70,
"Tivoli II." : 0.70,
"BS4" : 0.70,

"Trg prekomorskih brigad" : 0.60,
"Žale I." : 0.60,
"Žale II." : 0.60,
"Žale III." : 0.60,
"Žale IV." : 0.60,
"Žale V." : 0.60,
"Kranjčeva ulica" : 0.60,
"Gosarjeva ulica" : 0.60,
"Povšetova ulica" : 0.60,
"Slovenčeva ulica" : 0.60,
"Dolenjska cesta (Strelišče)" : 0.60,
"Tacen" : 0.60,
"Pokopališče Polje" : 0.60,
"Komanova ulica" : 0.60,
"Pot Roberta Blinca" : 0.60,
"ZOO" : 0.60,

"PH Kolezija" : 1.20,
"PH Kongresni trg" : 1.20,
"PH Rog" : 1.20,
"Kozolec" : 1.20,

"Linhartova" : 1.00,
}

df = pd.read_csv("../podatki/parking_data.csv")
df = df[(df["Prosto"] != "/") & (~df["Prosto"].isna())]
df["Prosto"] = pd.to_numeric(df["Prosto"])
df["Na voljo"] = pd.to_numeric(df["Na voljo"])
df["Zasedenost"] = (1 -(df["Prosto"]  / df["Na voljo"])) * 100
mask = df['Zasedenost'] < 0
df.loc[mask, 'Zasedenost'] = 0
short = df[["Location", "Prosto", "Na voljo", "Zasedenost"]]
zasedenost = short.groupby("Location").agg("mean")
a = zasedenost.iloc[:, 2].to_list()
b = zasedenost.index.to_list()
b = [cene[x] for x in b]
print(a)
print(b)
print(zasedenost)


plt.scatter(a, b, s=5)
plt.ylabel("Cena parkirišča na uro [€/h]")
plt.xlabel("Povprečna zasedenost parkirišča [%]")
plt.show()