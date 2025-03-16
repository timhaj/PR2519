import requests
from bs4 import BeautifulSoup
import csv
import datetime
import re
import os
import time

def scrape_parking_data():
    url = "https://www.lpt.si/parkirisca/informacije-za-parkiranje/prikaz-zasedenosti-parkirisc"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Failed to retrieve the webpage")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.select_one("div.blocks div.block-item table")
    update_time_element = soup.select_one("div.blocks div.block-item p")

    if not table or not update_time_element:
        print("Required elements not found")
        return

    update_time_match = re.search(r"(\d{2}):(\d{2})", update_time_element.get_text())
    if update_time_match:
        hour, minute = update_time_match.groups()
        now = datetime.datetime.now()
        formatted_date = now.replace(hour=int(hour), minute=int(minute)).strftime("%Y-%m-%d %H:%M")
    else:
        formatted_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    data = []
    for row in table.select("tbody tr"):
        cols = row.find_all("td")
        if len(cols) < 2:
            continue

        location = cols[0].find("a").get_text(strip=True) if cols[0].find("a") else ""
        flex_div = cols[1].find("div", class_="flex")
        details = [p.get_text(strip=True) for p in flex_div.find_all("p")] if flex_div else ["", "", ""]

        data.append([location] + details + [formatted_date])

    file_path = "parking_data.csv"
    file_exists = os.path.exists(file_path)

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Location", "Status", "Prosto", "Na voljo", "Datum"])
        writer.writerows(data)

    print(f"[{formatted_date}] Data successfully appended to parking_data.csv")


if __name__ == "__main__":
    while True:
        scrape_parking_data()
        time.sleep(120)