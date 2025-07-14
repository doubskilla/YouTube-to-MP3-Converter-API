import requests

def main():
    try:
        response = requests.get("https://www.youtube.com", timeout=10)
        print("Statut de la requête vers YouTube :", response.status_code)
    except Exception as e:
        print("Erreur de connexion :", e)

if __name__ == "__main__":
    main()
