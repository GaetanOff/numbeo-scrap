import pandas as pd
import requests
from bs4 import BeautifulSoup

villes_france = pd.read_csv('../villes.csv')["ville"].tolist()


def getQualityIndices(soup, city):
    data = []

    sections = soup.find_all("div", class_="innerWidth")

    for section in sections:
        rows = section.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                index_name = cols[0].get_text(strip=True).replace(":", "")
                index_value = cols[1].get_text(strip=True)
                index_level = cols[2].get_text(strip=True) if len(cols) >= 3 else "N/A"
                data.append({
                    "Ville": city,
                    "Indice": index_name,
                    "Valeur": index_value,
                    "Niveau": index_level
                })
    return data


def getAllCitiesQuality(citiesList):
    df = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }

    for city in citiesList:
        city_url = city.replace(" ", "-")
        url = f'https://www.numbeo.com/quality-of-life/in/{city_url}'
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            print(f"✅ Données récupérées pour {city}")
        except requests.RequestException:
            print(f"❌ Erreur de connexion pour {city}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        city_data = getQualityIndices(soup, city)
        df.extend(city_data)

    return df


all_quality_data = getAllCitiesQuality(villes_france)

df = pd.DataFrame(all_quality_data)

df.to_csv("data/villes_qualite_vie_complet.csv", index=False, encoding='utf-8-sig')

print("✅ Le fichier CSV complet avec les indices de qualité de vie a été généré avec succès.")
