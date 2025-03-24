import pandas as pd
import requests
from bs4 import BeautifulSoup


def parse_float(value_str):
    if not value_str:
        return None
    cleaned = (
        value_str.replace(",", ".")
        .replace("(", "")
        .replace(")", "")
        .strip()
    )
    try:
        return float(cleaned)
    except ValueError:
        return None


def get_quality_indices(soup, city):
    data = []
    sections = soup.find_all("div", class_="innerWidth")
    for section in sections:
        rows = section.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                index_name = cols[0].get_text(strip=True).replace(":", "")
                index_value = parse_float(cols[1].get_text(strip=True))
                index_level = cols[2].get_text(strip=True) if len(cols) >= 3 else "N/A"
                data.append({
                    "Ville": city,
                    "Indice": index_name,
                    "Valeur": index_value,
                    "Niveau": index_level
                })
    return data


def scrape_quality(cities_list, output_csv="data/villes_qualite_vie_raw.csv"):
    df_list = []
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/117.0.0.0 Safari/537.36"
        )
    }
    for city in cities_list:
        city_url = city.replace(" ", "-")
        url = f"https://www.numbeo.com/quality-of-life/in/{city_url}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            print(f"✅ Données récupérées pour {city}")
        except requests.RequestException:
            print(f"❌ Erreur de connexion pour {city}")
            continue
        soup = BeautifulSoup(response.content, "html.parser")
        city_data = get_quality_indices(soup, city)
        df_list.extend(city_data)
    df = pd.DataFrame(df_list)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"✅ Le fichier CSV brut '{output_csv}' a été généré avec succès.")


if __name__ == "__main__":
    villes_france = pd.read_csv("../villes.csv")["ville"].tolist()
    scrape_quality(villes_france)
