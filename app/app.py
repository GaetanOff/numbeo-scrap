import subprocess
import sys

def main():
    python_exec = sys.executable
    while True:
        print("\nSélecteur d'exécution :")
        print("1. Lancer le scrap")
        print("2. Lancer l'ETL")
        print("3. Lancer le ML")
        print("4. Quitter")
        choice = input("Entrez votre choix (1, 2, 3 ou 4) : ").strip()

        if choice == "1":
            print("Lancement du scrap...")
            subprocess.run([python_exec, "scrap/costOfLife.py"])
            subprocess.run([python_exec, "scrap/qualityOfLive.py"])
        elif choice == "2":
            print("Lancement de l'ETL...")
            subprocess.run([python_exec, "etl/etl.py"])
        elif choice == "3":
            print("Lancement du ML...")
            subprocess.run([python_exec, "ml/ml.py"])
        elif choice == "4":
            print("Au revoir!")
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

if __name__ == "__main__":
    main()
