import pandas as pd
import streamlit as st
import os
from datetime import datetime, time
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "podatki")
path_delo = os.path.join(DATA_DIR, "parking_data.csv")
path_delo2 = os.path.join(DATA_DIR, "parking_data2.csv")

IMAGE_DIR = os.path.join(BASE_DIR, "slike")
path_slika_tab2 = os.path.join(IMAGE_DIR, "primer3.png")

st.title("Napovedni model zasedenosti parkirišč")

st.balloons()

section = st.sidebar.radio("", ["Predstavitev", "Analiza", "Napoved"])

if section == "Predstavitev":
    st.header("Predstavitev")
    st.markdown("""
            ### Uvod 
            V tem projektu nas je zanimalo, kakšna je zasedenost parkirišč v Mestni občini Ljubljana (MOL), saj smo želeli na podlagi podatkov ugotoviti, kdaj imamo največ možnosti za uspešno iskanje parkirnega mesta.
            
            ### O podatkih
            Naredili smo "web-scraperja", ki vsakih 15 minut pridobi podatke s spletne strani [mestne občine ljubljana](https://www.lpt.si/parkirisca/informacije-za-parkiranje/prikaz-zasedenosti-parkirisc),
            podatke smo shranjevali v .csv datoteko.
            
            Zajeti podatki vključujejo:
            
            - ime parkirišča,
            - status (odprto/zaprto),
            - število prostih mest,
            - skupno število mest,
            - datum in čas zajema.
            
            Poleg tega smo imeli na voljo še pdf datoteko Cenik, v katerem so shranjeni podatki o tarifah za posamezno parkirišče.
            Za zajem podatkov smo uporabili knjižnico BeautifulSoup.
            Do pisanja tega vmesnega poročila smo uspeli zbrati že precej podatkov. Zajem smo začeli 18. 3. 2025, podatki pa segajo do 10. 4. 2025.
            
            Preden smo začeli podatke uporabljati smo ugotovili da jih za nekaj parkirišč na spletni strani ni zapisano mesto prostih in na voljo, ampak je namesto tega pisalo le "/". Tudi o nekaterih drugih parkiriščih je spletna stran pisala le status zasedenosti brez številskih podatkov, zato smo vrstice za ta parkirišča odstranili.
            Poleg tega smo med potekom naloge ugotovili da so ob nekatrih časih zapisane nelogične vrednosti - število prostih mest je bilo večje od števila vseh parkirnih mest. To smo popravili tako, da smo število prostih mest zgoraj omejili z številom parkirišč.        
    """)

elif section == "Analiza":
    st.header("Izvedene analize")
    tab1, tab2, tab3, tab4 = st.tabs(["Dnevna zasedenost parkirišča", "Skupno število prostih mest", "Vpliv cen parkiranja", "Tedenska porazdelitev zasedenosti"])

######################## TAB 1 ################################

    df = pd.read_csv(path_delo)
    df2 = pd.read_csv(path_delo2)
    df = pd.concat([df, df2])
    df = df[(df["Prosto"] != "/") & (~df["Prosto"].isna()) & (df["Location"] != "Slovenčeva ulica")]
    base_date = pd.to_datetime("1970-01-01")
    selected_location = tab1.selectbox(
        "Izberi parkirišče: ",
        tuple(df["Location"].unique()),
    )
    tab1.header(f"Povprečna dnevna zasedenost za parkirišče: {selected_location}")
    p = df[df["Location"] == selected_location].copy()
    p["Datum"] = pd.to_datetime(p["Datum"])
    all_days_data = []
    for day in pd.date_range(start="2025-03-18", end="2025-05-30"):
        day_data = p[(p["Datum"] >= day) & (p["Datum"] < day + pd.Timedelta(days=1))].copy()
        if str(day) in ["2025-03-29 00:00:00", "2025-04-05 00:00:00", "2025-04-07 00:00:00", "2025-04-08 00:00:00",
                        "2025-04-09 00:00:00"]:
            continue
        day_data["Time"] = base_date + (day_data["Datum"].dt.hour * pd.Timedelta(hours=1)) + (
                day_data["Datum"].dt.minute * pd.Timedelta(minutes=1))
        day_data["Normalized"] = 100 - (day_data["Prosto"].astype(int) / day_data["Na voljo"].astype(int) * 100)
        all_days_data.append(day_data[["Time", "Normalized"]])
    combined = pd.concat(all_days_data)
    combined['To15min'] = combined['Time'].dt.round('15min').dt.time.apply(
        lambda t: datetime.datetime.combine(datetime.datetime(1970, 1, 1), t))
    combined = combined[["To15min", "Normalized"]]
    avg_data = combined.groupby("To15min").mean().reset_index()
    mask = avg_data['Normalized'] < 0
    avg_data.loc[mask, 'Normalized'] = 0
    avg_data.index = avg_data["To15min"]
    avg_data.index = avg_data["To15min"].dt.strftime("%H:%M")  # Format as "00:00", "00:15", etc.
    avg_data = avg_data[["Normalized"]]
    tab1.line_chart(avg_data, height=250)

########################### TAB 2 ################################

    tab2.write("Spodnji graf prikazuje skupno število prostih mest skozi vse dni beleženja. Modro ozadje označuje vikende.")
    tab2.image(path_slika_tab2)
    tab2.write("Opazimo, da je največ prostih parkirnih mest zgodaj zjutraj, medtem ko je okoli poldneva dosežena najvišja zasedenost.")

########################## TAB 3 #################################

    cene = {
        "Sanatorij Emona": 1.20,
        "Metelkova ulica": 1.20,
        "Krekov trg": 1.20,

        "Bežigrad": 0.70,
        "Gospodarsko razstavišče": 0.70,
        "Mirje": 0.70,
        "Trg mladinskih delovnih brigad": 0.70,
        "Tivoli I.": 0.70,
        "Tivoli II.": 0.70,
        "BS4": 0.70,

        "Trg prekomorskih brigad": 0.60,
        "Žale I.": 0.60,
        "Žale II.": 0.60,
        "Žale III.": 0.60,
        "Žale IV.": 0.60,
        "Žale V.": 0.60,
        "Kranjčeva ulica": 0.60,
        "Gosarjeva ulica": 0.60,
        "Povšetova ulica": 0.60,
        "Slovenčeva ulica": 0.60,
        "Dolenjska cesta (Strelišče)": 0.60,
        "Tacen": 0.60,
        "Pokopališče Polje": 0.60,
        "Komanova ulica": 0.60,
        "Pot Roberta Blinca": 0.60,
        "ZOO": 0.60,

        "PH Kolezija": 1.20,
        "PH Kongresni trg": 1.20,
        "PH Rog": 1.20,
        "Kozolec": 1.20,

        "Linhartova": 1.00,
    }
    df = pd.read_csv(path_delo)
    df2 = pd.read_csv(path_delo2)
    df = pd.concat([df, df2])
    df = df[(df["Prosto"] != "/") & (~df["Prosto"].isna())]
    df["Prosto"] = pd.to_numeric(df["Prosto"])
    df["Na voljo"] = pd.to_numeric(df["Na voljo"])
    df["Zasedenost"] = (1 - (df["Prosto"] / df["Na voljo"])) * 100
    mask = df['Zasedenost'] < 0
    df.loc[mask, 'Zasedenost'] = 0
    short = df[["Location", "Prosto", "Na voljo", "Zasedenost"]]
    zasedenost = short.groupby("Location").agg("mean")
    a = zasedenost.iloc[:, 2].to_list()
    b = zasedenost.index.to_list()
    b = [cene[x] for x in b]
    zasedenost.index = b
    zasedenost = zasedenost[["Zasedenost"]]
    tmp = zasedenost["Zasedenost"].values
    zasedenost["Zasedenost"] = zasedenost.index
    zasedenost.index = tmp
    zasedenost = zasedenost.rename(columns={"Zasedenost": "Cena"})
    tab3.write("Na grafu spodaj je na y-osi prikazana cena za 1 uro parkiranja, na x-osi pa povprečna zasedenost parkirišča (v odstotkih) skozi vse dni beleženja.")
    tab3.scatter_chart(zasedenost)
    tab3.write("Iz grafa lahko razberemo, da kljub nizki ceni parkiranja zasedenost na mnogih parkiriščih ni visoka. V spodnjem desnem delu grafa se pojavi nenavaden primer – eno parkirišče je ves čas prikazano kot polno. To skoraj zagotovo kaže na napako v podatkih (verjetno težava s senzorjem). V zgornjem desnem delu se pojavi skupina parkirišč z visoko ceno in hkrati visoko zasedenostjo – med njimi sta tudi Sanatorij Emona in Metelkova ulica, ki sta znani in dobro obiskani lokaciji. Na tej podlagi sklepamo, da ima na zasedenost večji vpliv lokacija, ne pa nujno cena parkiranja.")

########################### TAB 4 ################################

    days = ["pon", "tor", "sre", "čet", "pet", "sob", "ned"]
    df = pd.read_csv(path_delo)
    df2 = pd.read_csv(path_delo2)
    df = pd.concat([df, df2])
    df = df[(df["Prosto"] != "/") & (~df["Prosto"].isna())]
    df["Prosto"] = pd.to_numeric(df["Prosto"])
    df["Na voljo"] = pd.to_numeric(df["Na voljo"])
    df["Zasedenost"] = (1 -(df["Prosto"] / df["Na voljo"])) * 100
    df["Datum"] = pd.to_datetime(df["Datum"])
    df["Datum"] = df["Datum"].dt.day_of_week
    mask = df['Zasedenost'] < 0
    df.loc[mask, 'Zasedenost'] = 0
    short = df[["Datum", "Prosto", "Na voljo", "Zasedenost"]]
    zasedenost = short.groupby("Datum").agg("mean")
    zasedenost = zasedenost[["Zasedenost"]]
    zasedenost.index = days
    zasedenost.index = pd.Categorical(
        zasedenost.index,
        categories=days,
        ordered=True
    )
    tab4.write("Na grafu je prikazana povprečna zasedenost po dnevih v tednu za celotno zajeto obdobje.")
    tab4.bar_chart(zasedenost, x=None)
    tab4.write("Kot pričakovano so vikendi – še posebej nedelje – najmanj zasedeni dnevi v tednu. Parkirišča pa so najbolj polna ob četrtkih Pri teh podatkih pa bodimo pozorni, da je to celodnevno povprečje. Stopnja zasedenosti bi bila precej višja če bi upoštevali le časovni interval od 7:00-19:00 ko so parkirišča najbolj polna, kar lahko vidimo že iz iz 1. in 2. slike, ki predstavljata zasedenost parkirišč skozi čas.")

elif section == "Napoved":
    st.header("Napovedni model")

    df = pd.read_csv(path_delo)
    df2 = pd.read_csv(path_delo2)
    df = pd.concat([df, df2])
    df = df[(df["Prosto"] != "/") & (~df["Prosto"].isna()) & (df["Location"] != "Slovenčeva ulica")]
    base_date = pd.to_datetime("1970-01-01")
    col1, col2, col3, col4 = st.columns(4)
    selected_date = col1.date_input("Izberi datum")

    now = datetime.datetime.now()
    rounded_minute = ((now.minute + 14) // 15) * 15
    if rounded_minute >= 60:
        rounded_minute = 0
        now += datetime.timedelta(hours=1)
    rounded_time = now.replace(minute=rounded_minute, second=0, microsecond=0).time()

    selected_time = col2.time_input("Izberi časovno okno", value=rounded_time)
    selected_location = col3.selectbox(
        "Izberi parkirišče",
        tuple(df["Location"].unique())
    )

    st.markdown(
        """
        <style>
        .stHorizontalBlock.st-emotion-cache-ocqkz7.e1lln2w80 > div:nth-child(4) {
            margin-top: auto !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if col4.button("Napovej", type="primary"):
        p = df[df["Location"] == selected_location].copy()
        p["Datum"] = pd.to_datetime(p["Datum"])
        all_days_data = []
        for day in pd.date_range(start="2025-03-18", end="2025-05-30"):
            day_data = p[(p["Datum"] >= day) & (p["Datum"] < day + pd.Timedelta(days=1))].copy()
            if str(day) in ["2025-03-29 00:00:00", "2025-04-05 00:00:00", "2025-04-07 00:00:00", "2025-04-08 00:00:00",
                            "2025-04-09 00:00:00"]:
                continue
            day_data["Time"] = base_date + (day_data["Datum"].dt.hour * pd.Timedelta(hours=1)) + (
                    day_data["Datum"].dt.minute * pd.Timedelta(minutes=1))
            day_data["Normalized"] = 100 - (day_data["Prosto"].astype(int) / day_data["Na voljo"].astype(int) * 100)
            all_days_data.append(day_data[["Time", "Normalized"]])
        combined = pd.concat(all_days_data)
        combined['To15min'] = combined['Time'].dt.round('15min').dt.time.apply(
            lambda t: datetime.datetime.combine(datetime.datetime(1970, 1, 1), t))
        combined = combined[["To15min", "Normalized"]]
        avg_data = combined.groupby("To15min").mean().reset_index()
        mask = avg_data['Normalized'] < 0
        avg_data.loc[mask, 'Normalized'] = 0
        avg_data.index = avg_data["To15min"]
        avg_data = avg_data[["Normalized"]]
        val = avg_data.loc[selected_time]
        val = round((1 - (val/100)) * 100,2)
        val = val['Normalized'].values[0]
        color_map = {
            "red": "#D72A1D",
            "yellow": "#FFFA5C",
            "green": "#87D68D"
        }

        if val < 20:
            color = color_map["red"]
        elif 20 <= val <= 70:
            color = color_map["yellow"]
        else:
            color = color_map["green"]

        st.markdown(
            f'<span style="color:{color}; font-weight:bold;">Napovedana razpoložljivost parkirišča za vse dni v tednu: {val}%</span>',
            unsafe_allow_html=True
        )

        day_of_the_week = pd.to_datetime(selected_date).strftime("%A")
        p = df[df["Location"] == selected_location].copy()
        p["Datum"] = pd.to_datetime(p["Datum"])
        p["DayOfWeek"] = p["Datum"].dt.strftime("%A")
        p = p[p["DayOfWeek"] == day_of_the_week]
        all_days_data = []
        for day in pd.date_range(start="2025-03-18", end="2025-05-30"):
            day_data = p[(p["Datum"] >= day) & (p["Datum"] < day + pd.Timedelta(days=1))].copy()
            if str(day) in ["2025-03-29 00:00:00", "2025-04-05 00:00:00", "2025-04-07 00:00:00", "2025-04-08 00:00:00",
                            "2025-04-09 00:00:00"]:
                continue
            day_data["Time"] = base_date + (day_data["Datum"].dt.hour * pd.Timedelta(hours=1)) + (
                    day_data["Datum"].dt.minute * pd.Timedelta(minutes=1))
            day_data["Normalized"] = 100 - (day_data["Prosto"].astype(int) / day_data["Na voljo"].astype(int) * 100)
            all_days_data.append(day_data[["Time", "Normalized"]])
        combined = pd.concat(all_days_data)
        combined['To15min'] = combined['Time'].dt.round('15min').dt.time.apply(
            lambda t: datetime.datetime.combine(datetime.datetime(1970, 1, 1), t))
        combined = combined[["To15min", "Normalized"]]
        avg_data = combined.groupby("To15min").mean().reset_index()
        mask = avg_data['Normalized'] < 0
        avg_data.loc[mask, 'Normalized'] = 0
        avg_data.index = avg_data["To15min"]
        avg_data = avg_data[["Normalized"]]
        val = avg_data.loc[selected_time]
        val = round((1 - (val/100)) * 100,2)
        val = val['Normalized'].values[0]
        if val < 20:
            color = color_map["red"]
        elif 20 <= val <= 70:
            color = color_map["yellow"]
        else:
            color = color_map["green"]

        st.markdown(
            f'<span style="color:{color}; font-weight:bold;">Napovedana razpoložljivost parkirišča glede na dan: {val}%</span>',
            unsafe_allow_html=True
        )
