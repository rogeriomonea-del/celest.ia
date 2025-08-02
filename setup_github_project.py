import requests
import os
from dotenv import load_dotenv

# === CONFIGURAÇÃO NECESSÁRIA ===
load_dotenv()  # Carrega variáveis do .env

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

REPO_OWNER = "rogeriomonea-del"
REPO_NAME = "celest.ia"
PROJECT_NAME = "Celes.ia v2 Alpha"
API_URL = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.inertia-preview+json"
}

def create_project():
    url = f"{API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/projects"
    data = {"name": PROJECT_NAME, "body": "Gerado automaticamente pelo setup script"}
    r = requests.post(url, headers=HEADERS, json=data)
    r.raise_for_status()
    return r.json()["id"]

def create_column(project_id, column_name):
    url = f"{API_URL}/projects/{project_id}/columns"
    data = {"name": column_name}
    r = requests.post(url, headers=HEADERS, json=data)
    r.raise_for_status()
    return r.json()["id"]

def create_card(column_id, note):
    url = f"{API_URL}/projects/columns/{column_id}/cards"
    data = {"note": note}
    r = requests.post(url, headers=HEADERS, json=data)
    r.raise_for_status()

def main():
    project_id = create_project()

    columns = {
        "Backlog": ["Scraping LATAM/Copa", "Exportação de planilhas"],
        "Em progresso": ["Painel dashboard", "Deploy Railway/VPS"],
        "Testes": ["Self-healing da IA"],
        "Concluído": []
    }

    for col_name, cards in columns.items():
        col_id = create_column(project_id, col_name)
        for card in cards:
            create_card(col_id, card)

    print("✅ Projeto criado com sucesso!")

if __name__ == "__main__":
    main()
