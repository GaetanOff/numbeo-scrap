import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# 1. Charger les datasets nettoyés
df_prices = pd.read_csv("data/cleaned/villes_produits_prix_clean.csv")
df_city = pd.read_csv("data/cleaned/villes_final_ml.csv")

# 2. Fusionner les données sur la colonne "Ville"
df = pd.merge(df_prices, df_city, on="Ville", how="inner")
print("Shape du dataset fusionné:", df.shape)
print(df.head())

# 3. Préparation des features

# Liste des features issus du dataset des villes (données agrégées)
city_features = [
    "PrixMoyenGlobal",
    "Climate Index",
    "Cost of Living Index",
    "Health Care Index",
    "Pollution Index",
    "Property Price to Income Ratio",
    "Purchasing Power Index",
    "Quality of Life Index",
    "Safety Index",
    "Traffic Commute Time Index"
]

# Conversion en numérique et remplissage des valeurs manquantes avec la moyenne
for col in city_features:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].mean())

# Transformation de la variable catégorielle "Produit" en variables dummy
df = pd.get_dummies(df, columns=["Produit"], drop_first=True)

# Définir la target : le prix moyen du produit dans la ville
target = "PrixMoyen"

# Les features seront les indices de la ville et les variables dummy pour le produit
dummy_cols = [col for col in df.columns if col.startswith("Produit_")]
feature_cols = city_features + dummy_cols

X = df[feature_cols]
y = df[target]

# 4. Séparation en données d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Entraînement du modèle principal
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Entraîner un modèle de repli utilisant uniquement les indices de la ville
X_train_city = X_train[city_features]
fallback_model = RandomForestRegressor(n_estimators=100, random_state=42)
fallback_model.fit(X_train_city, y_train)

# 6. Évaluation du modèle principal
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print("\nÉvaluation du modèle principal:")
print("Erreur quadratique moyenne (MSE): {:.2f}".format(mse))
print("Coefficient de détermination (R²): {:.2f}".format(r2))

plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, color="blue", alpha=0.7)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "r--", lw=2)
plt.xlabel("Prix réel")
plt.ylabel("Prix prédit")
plt.title("Comparaison entre prix réel et prédit")
plt.show()


# 7. Fonction de prédiction pour un nouveau produit dans une ville donnée
def predict_price(model, fallback_model, df_city, city_features, dummy_cols, feature_cols, city, product):
    """
    Prédit le prix d'un produit dans une ville.
    - city: nom de la ville (ex: "Montpellier")
    - product: nom du produit tel que fourni par l'utilisateur (ex: "Banane")

    Une étape de normalisation du nom du produit est appliquée via product_mapping.
    Si le produit n'est pas présent dans l'entraînement,
    on utilise fallback_model qui se base uniquement sur les indices de la ville.
    """
    # Dictionnaire de correspondance pour normaliser le nom du produit
    product_mapping = {
        "banane": "Banana (1kg)",
        # Ajouter d'autres correspondances si nécessaire :
        # "souris d'ordinateur": "Computer Mouse",
    }

    # Normaliser le nom du produit : passage en minuscule et recherche dans le mapping
    product_norm = product.strip().lower()
    if product_norm in product_mapping:
        product_final = product_mapping[product_norm]
    else:
        product_final = product  # On garde le nom fourni si aucune correspondance n'est trouvée

    # Récupérer les indices de la ville depuis le dataset des villes
    city_row = df_city[df_city["Ville"] == city]
    if city_row.empty:
        print(f"Ville '{city}' non trouvée dans le dataset.")
        return None

    # Récupérer les valeurs des indices de la ville
    features = {col: float(city_row.iloc[0][col]) for col in city_features}

    # Initialiser toutes les variables dummy à 0
    for col in dummy_cols:
        features[col] = 0

    # Nom de la variable dummy pour le produit
    dummy_name = "Produit_" + product_final
    if dummy_name in dummy_cols:
        features[dummy_name] = 1
        # Utiliser le modèle principal
        X_new = pd.DataFrame([features])[feature_cols]
        pred_price = model.predict(X_new)[0]
        print(f"Produit '{product_final}' présent dans l'entraînement.")
    else:
        print(
            f"Attention: Le produit '{product_final}' n'est pas présent dans l'entraînement. Utilisation du modèle de repli.")
        # Utiliser uniquement les indices de la ville pour la prédiction
        X_new = pd.DataFrame([features])[city_features]
        pred_price = fallback_model.predict(X_new)[0]

    return pred_price


# Exemple de prédiction : prix d'une 'Banane' à Montpellier
city_to_predict = "Montpellier"
product_to_predict = "Banane"  # L'utilisateur fournit "Banane", qui est converti en "Banana (1kg)"
predicted_price = predict_price(model, fallback_model, df_city, city_features, dummy_cols, feature_cols,
                                city_to_predict, product_to_predict)
if predicted_price is not None:
    print(f"\nLe prix prédit pour une '{product_to_predict}' à {city_to_predict} est de {predicted_price:.2f} €")
