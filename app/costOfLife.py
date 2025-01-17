import pandas as pd
import requests
from bs4 import BeautifulSoup

villes_france = pd.read_csv('../villes.csv')["ville"].tolist()


def getPrice(td):
    results = []
    next_td = td.find_next_sibling("td", class_="priceBarTd")
    if next_td:
        span_left = next_td.find("span", class_="barTextLeft")
        span_right = next_td.find("span", class_="barTextRight")
        if span_left and span_right:
            results.append((span_left.text.strip(), span_right.text.strip()))
    return results


def getAveragePrice(price1, price2):
    try:
        return round((float(price1.replace(",", ".")) + float(price2.replace(",", "."))) / 2, 2)
    except ValueError:
        return None


def getAllProductsInCities(citiesList):
    data = []
    for city in citiesList:
        city_url = city.replace(" ", "-")
        url = f'https://www.numbeo.com/cost-of-living/in/{city_url}'
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            print(f"❌ Erreur de connexion pour {city}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        product_rows = soup.find_all("tr")
        for row in product_rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                product_name = cols[0].text.strip()
                results = getPrice(cols[0])
                for left, right in results:
                    average_price = getAveragePrice(left, right)
                    if average_price is not None:
                        print(f"✅ {product_name} à {city} : {average_price}€")
                        data.append({
                            "Produit": product_name,
                            "Ville": city,
                            "Prix (€)": average_price
                        })
    return data


all_prices_data = getAllProductsInCities(villes_france)

df = pd.DataFrame(all_prices_data)

df.to_csv("data/villes_produits_prix.csv", index=False, encoding='utf-8-sig')

print("✅ Le fichier CSV global a été généré avec succès.")
