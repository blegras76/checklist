import streamlit as st
import requests
import json
import base64
import pandas as pd

# Paramètres de connexion GitHub
GITHUB_TOKEN = 'ghp_votre_token_github'
REPO_OWNER = 'votre_nom_utilisateur'
REPO_NAME = 'nom_du_depot'
BRANCH_NAME = 'main'  # ou 'master' si c'est le cas

# Fonction pour envoyer un fichier CSV sur GitHub
def upload_to_github(file_path, content):
    """Envoie ou met à jour un fichier sur un dépôt GitHub privé"""
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}'
    
    # Vérifiez si le fichier existe
    response = requests.get(url, headers={'Authorization': f'token {GITHUB_TOKEN}'})
    if response.status_code == 200:
        sha = response.json()['sha']
    else:
        sha = None

    # Encoder le contenu en base64
    encoded_content = base64.b64encode(content.encode()).decode('utf-8')
    data = {
        'message': 'Mise à jour du fichier CSV',
        'content': encoded_content,
        'branch': BRANCH_NAME
    }
    if sha:
        data['sha'] = sha  # Nécessaire pour mettre à jour un fichier existant

    response = requests.put(url, headers={'Authorization': f'token {GITHUB_TOKEN}'}, data=json.dumps(data))
    return response.status_code, response.json()

# Fonction pour récupérer un fichier CSV depuis GitHub
def download_from_github(file_path):
    """Télécharge un fichier CSV depuis le dépôt GitHub"""
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        file_content = base64.b64decode(response.json()['content'])
        return file_content.decode('utf-8')
    else:
        st.error(f"Erreur lors du téléchargement du fichier : {response.status_code}")
        return None

# ---- Interface utilisateur Streamlit ----
st.title("Téléverser et récupérer des fichiers CSV depuis GitHub")

# Upload d'un fichier CSV
uploaded_file = st.file_uploader("Choisissez un fichier CSV à téléverser", type=["csv"])
if uploaded_file is not None:
    content = uploaded_file.read().decode('utf-8')
    if st.button("Envoyer le fichier CSV sur GitHub"):
        file_path = f"data/{uploaded_file.name}"  # Chemin sur GitHub
        status_code, response = upload_to_github(file_path, content)
        
        if status_code in [200, 201]:
            st.success(f"Fichier {uploaded_file.name} sauvegardé sur GitHub avec succès !")
        else:
            st.error(f"Erreur lors de l'envoi sur GitHub : {response}")

# Récupérer un fichier CSV
st.header("Récupérer un fichier CSV depuis GitHub")
filename = st.text_input("Entrez le nom du fichier (ex : 'data/mon_fichier.csv')", value="data/checklist.csv")
if st.button("Télécharger le fichier CSV"):
    content = download_from_github(filename)
    if content:
        st.success("Fichier téléchargé avec succès !")
        df = pd.read_csv(pd.compat.StringIO(content))
        st.write(df)
