import pandas as pd
import requests
from bs4 import BeautifulSoup


def parse_price_value(value_str):
    if not value_str:
        return None
    clean_str = (
        value_str.replace(",", ".")
        .replace("€", "")
        .replace(" ", "")
        .strip()
    )
    try:
        return float(clean_str)
    except ValueError:
        return None


def get_price_range(td):
    price_bar = td.find_next_sibling("td", class_="priceBarTd")
    if not price_bar:
        return None, None, None
    span_left = price_bar.find("span", class_="barTextLeft")
    span_right = price_bar.find("span", class_="barTextRight")
    if span_left and span_right:
        price_min = parse_price_value(span_left.text)
        price_max = parse_price_value(span_right.text)
        if price_min is not None and price_max is not None:
            return price_min, price_max, round((price_min + price_max) / 2, 2)
    return None, None, None


def scrape_prices(cities_list, output_csv="data/villes_produits_prix_raw.csv"):
    data = []
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/117.0.0.0 Safari/537.36"
        )
    }
    for city in cities_list:
        city_url = city.replace(" ", "-")
        url = f"https://www.numbeo.com/cost-of-living/in/{city_url}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            print(f"❌ Erreur de connexion pour {city}")
            continue
        soup = BeautifulSoup(response.content, "html.parser")
        product_rows = soup.find_all("tr")
        for row in product_rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                product_name = cols[0].get_text(strip=True)
                price_min, price_max, price_avg = get_price_range(cols[0])
                if price_avg is not None:
                    print(f"✅ {product_name} à {city} : {price_min}-{price_max} => {price_avg} €")
                    data.append({
                        "Ville": city,
                        "Produit": product_name,
                        "PrixMin": price_min,
                        "PrixMax": price_max,
                        "PrixMoyen": price_avg
                    })
    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"✅ Le fichier CSV brut '{output_csv}' a été généré avec succès.")


if __name__ == "__main__":
    villes_france = pd.read_csv("../villes.csv")["ville"].tolist()
    scrape_prices(villes_france)
