import pandas as pd


def clean_prices(input_csv="data/villes_produits_prix_raw.csv",
                 output_csv="data/cleaned/villes_produits_prix_clean.csv"):
    # Charger les données raw
    df = pd.read_csv(input_csv)

    # Standardiser les noms de colonnes (supprimer espaces en trop)
    df.columns = [col.strip() for col in df.columns]

    # Conversion des colonnes de prix en float
    for col in ["PrixMin", "PrixMax", "PrixMoyen"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Suppression des doublons
    df.drop_duplicates(inplace=True)

    # Suppression des lignes avec des valeurs manquantes dans les colonnes critiques
    df.dropna(subset=["Ville", "Produit", "PrixMin", "PrixMax", "PrixMoyen"], inplace=True)

    # Filtrage des lignes avec des valeurs de prix incohérentes (inférieures ou égales à 0)
    df = df[(df["PrixMin"] > 0) & (df["PrixMax"] > 0) & (df["PrixMoyen"] > 0)]

    # Nettoyage des chaînes de caractères
    df["Ville"] = df["Ville"].str.strip()
    df["Produit"] = df["Produit"].str.strip()

    # Sauvegarder le CSV nettoyé
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    return df


def clean_quality(input_csv="data/villes_qualite_vie_raw.csv",
                  output_csv="data/cleaned/villes_qualite_vie_clean.csv"):
    # Charger les données raw
    df = pd.read_csv(input_csv)

    # Standardiser les noms de colonnes
    df.columns = [col.strip() for col in df.columns]

    # Supprimer les lignes dont les colonnes critiques sont manquantes
    df.dropna(subset=["Ville", "Indice", "Valeur"], inplace=True)

    # Supprimer les lignes où l'indice est vide ou non pertinent
    df = df[df["Indice"].str.strip() != ""]

    # Conversion de la colonne Valeur en float en gérant les virgules et en extrayant le nombre
    df["Valeur"] = (df["Valeur"]
                    .astype(str)
                    .str.replace(",", ".")
                    .str.extract(r'([\d\.]+)', expand=False))
    df["Valeur"] = pd.to_numeric(df["Valeur"], errors="coerce")

    # Suppression des lignes où la conversion a échoué
    df.dropna(subset=["Valeur"], inplace=True)

    # Filtrer pour ne conserver que les indices pertinents pour le ML
    valid_indices = [
        "Quality of Life Index",
        "Purchasing Power Index",
        "Safety Index",
        "Health Care Index",
        "Climate Index",
        "Cost of Living Index",
        "Property Price to Income Ratio",
        "Traffic Commute Time Index",
        "Pollution Index"
    ]
    df = df[df["Indice"].isin(valid_indices)]

    # Nettoyage des chaînes de caractères
    df["Ville"] = df["Ville"].str.strip()
    df["Indice"] = df["Indice"].str.strip()
    if "Niveau" in df.columns:
        df["Niveau"] = df["Niveau"].str.strip()

    # Suppression des doublons
    df.drop_duplicates(inplace=True)

    # Sauvegarder le CSV nettoyé
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    return df


def merge_clean_data(prices_csv="data/cleaned/villes_produits_prix_clean.csv",
                     quality_csv="data/cleaned/villes_qualite_vie_clean.csv",
                     output_csv="data/cleaned/villes_final_ml.csv"):
    # Charger les données nettoyées
    df_prices = pd.read_csv(prices_csv)
    df_quality = pd.read_csv(quality_csv)

    # Agréger les prix par ville : calculer le prix moyen global pour chaque ville
    agg_prices = (df_prices.groupby("Ville", as_index=False)
                  .agg({"PrixMoyen": "mean"})
                  .rename(columns={"PrixMoyen": "PrixMoyenGlobal"}))

    # Réorganiser le dataframe qualité de vie pour avoir un indice par colonne
    pivot_quality = (df_quality.pivot_table(index="Ville",
                                            columns="Indice",
                                            values="Valeur",
                                            aggfunc="mean")
                     .reset_index())

    # Fusionner les deux dataframes sur la colonne "Ville"
    df_final = pd.merge(agg_prices, pivot_quality, on="Ville", how="inner")

    # Optionnel : trier par ville
    df_final.sort_values("Ville", inplace=True)

    # Sauvegarder le fichier final pour le ML
    df_final.to_csv(output_csv, index=False, encoding="utf-8-sig")
    return df_final


if __name__ == "__main__":
    # ETL sur le fichier des prix
    prices_df = clean_prices()
    # ETL sur le fichier de qualité de vie
    quality_df = clean_quality()
    # Fusionner les données nettoyées pour obtenir un dataset final
    final_df = merge_clean_data()
    print("✅ ETL terminé. Fichiers nettoyés et fusionnés pour le ML.")
    print(final_df.head())
