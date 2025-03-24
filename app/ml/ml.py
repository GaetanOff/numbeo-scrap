import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# 1. Chargement des données
df_prix = pd.read_csv('data/villes_produits_prix.csv')
df_qualite = pd.read_csv('data/villes_qualite_vie_complet.csv')

# Vérifier si les fichiers CSV sont vides
if df_prix.empty or df_qualite.empty:
    print("❌ Les fichiers CSV sont vides. Merci de lancer le scrapping.")
    exit()

# Affichage des premières lignes pour voir la structure
print("Aperçu du fichier des prix:")
print(df_prix.head())
print("\nAperçu du fichier de qualité de vie:")
print(df_qualite.head())

# 2. Calcul du prix moyen par ville
# Dans df_prix, on utilise la colonne "Ville" et "Prix (€)"
df_prix_moyen = df_prix.groupby('Ville', as_index=False)['Prix (€)'].mean()
df_prix_moyen.rename(columns={'Prix (€)': 'prix_moyen'}, inplace=True)

# 3. Préparation des données de qualité de vie
# On filtre pour récupérer uniquement la ligne correspondant au "Quality of Life Index"
df_qualite_filtre = df_qualite[df_qualite['Indice'] == 'Quality of Life Index'][['Ville', 'Valeur']]
df_qualite_filtre.rename(columns={'Valeur': 'qualite_vie'}, inplace=True)

# 4. Fusion des deux jeux de données sur la colonne "Ville"
df = pd.merge(df_prix_moyen, df_qualite_filtre, on='Ville', how='inner')
print("\nAperçu du dataframe fusionné:")
print(df.head())

# 5. Préparation des variables pour la régression
X = df[['prix_moyen']]  # Variable prédictive
y = df['qualite_vie']   # Variable cible

# Séparation en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Création et entraînement du modèle de régression linéaire
model = LinearRegression()
model.fit(X_train, y_train)

# 6. Prédictions et évaluation
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\nÉvaluation du modèle:")
print("Erreur quadratique moyenne (MSE):", mse)
print("Coefficient de détermination (R2):", r2)

# Visualisation des résultats
plt.figure(figsize=(8, 6))
plt.scatter(X_test, y_test, color='blue', label='Valeurs réelles')
plt.plot(X_test, y_pred, color='red', linewidth=2, label='Prédiction')
plt.xlabel('Prix moyen')
plt.ylabel('Qualité de vie')
plt.title('Régression linéaire: Prix moyen vs Qualité de vie')
plt.legend()
plt.show()
