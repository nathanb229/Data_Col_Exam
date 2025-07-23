import streamlit as st
import pandas as pd
from requests import get # fonction permettant de récupérer le code html de la page
from bs4 import BeautifulSoup as bs # fonction permettant de stocker le code html en objet Beautifulsoup
from datetime import datetime
import re
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit.components.v1 as components


def scrapper_villas(paged, pagef):
    df = pd.DataFrame()

    for p in range(paged, pagef + 1):
        url = f'https://sn.coinafrique.com/categorie/villas?page={p}'
        res = get(url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all('div', class_='col s6 m4 l3')
        data = []

        for container in containers:
            try:
                lien_annonce = container.find('a', class_='card-image')['href']
                prix = container.find('p', class_='ad__card-price').text.replace(' ', '').replace('CFA', '')
                adresse = container.find('p', class_='ad__card-location').span.text.strip()
                image_lien = container.find('img', class_='ad__card-img')['src']
                type_annonce = container.find('p', class_='ad__card-description').text.strip().split()[0]

                # Aller dans la page de détail
                lien_complet = "https://sn.coinafrique.com" + lien_annonce
                res_detail = get(lien_complet)
                soup_detail = bs(res_detail.text, 'html.parser')
                details = soup_detail.find('div', class_='details-characteristics')

                nombre_pieces = None
                if details:
                    spans = details.find_all('span')
                    for i, span in enumerate(spans):
                        if span.text.strip() == "Nbre de pièces":
                            nombre_pieces = spans[i + 1].text.strip()
                            break

                obj = {
                    'type_annonce': type_annonce,
                    'nombre_pieces': nombre_pieces,
                    'prix': prix,
                    'adresse': adresse,
                    'image_lien': image_lien
                }
                data.append(obj)

            except Exception as e:
                continue

        DF = pd.DataFrame(data)
        df = pd.concat([df, DF], axis=0).reset_index(drop=True)

    return df

def scrapper_terrains(page_debut=1, page_fin=50):
    df = pd.DataFrame()
    date_scraping = datetime.today().strftime('%Y-%m-%d')

    for p in range(page_debut, page_fin + 1):
        url = f'https://sn.coinafrique.com/categorie/terrains?page={p}'
        res = get(url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all('div', class_='col s6 m4 l3')
        data = []

        for container in containers:
            try:
                # Texte brut description
                desc_text = container.find('p', class_='ad__card-description').text
                superficie_match = re.search(r'(\d+)', desc_text)
                superficie = int(superficie_match.group(1)) if superficie_match else None

                prix_raw = container.find('p', class_='ad__card-price').text
                prix = prix_raw.replace(' ', '').replace('CFA', '').replace(',', '').strip()

                adresse = container.find('p', class_='ad__card-location').span.text.strip()
                image_lien = container.find('img', class_='ad__card-img')['src']

                if superficie and prix.isdigit():
                    obj = {
                        'superficie': superficie,
                        'prix': int(prix),
                        'adresse': adresse,
                        'image_lien': image_lien,
                        'source': url,
                        'date_scraping': date_scraping
                    }
                    data.append(obj)

            except Exception as e:
                pass  # ou print(e) si tu veux le log

        df_page = pd.DataFrame(data)
        df = pd.concat([df, df_page], axis=0).reset_index(drop=True)

    return df

def scrapper_appartements(page_debut=1, page_fin=50):
    df = pd.DataFrame()
    date_scraping = datetime.today().strftime('%Y-%m-%d')

    for p in range(page_debut, page_fin + 1):
        url = f'https://sn.coinafrique.com/categorie/appartements?page={p}'
        res = get(url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all('div', class_='col s6 m4 l3')
        data = []

        for container in containers:
            try:
                lien_annonce = container.find('a', class_='card-image')['href']
                prix_raw = container.find('p', class_='ad__card-price').text
                prix = prix_raw.replace(' ', '').replace('CFA', '').replace(',', '').strip()
                adresse = container.find('p', class_='ad__card-location').span.text.strip()
                image_lien = container.find('img', class_='ad__card-img')['src']

                # Aller dans la page de détail
                lien_complet = "https://sn.coinafrique.com" + lien_annonce
                res_detail = get(lien_complet)
                soup_detail = bs(res_detail.text, 'html.parser')
                details = soup_detail.find('div', class_='details-characteristics')

                nombre_pieces = None
                if details:
                    spans = details.find_all('span')
                    for i, span in enumerate(spans):
                        if span.text.strip() == "Nbre de pièces":
                            nombre_pieces = spans[i + 1].text.strip()
                            break

                if nombre_pieces is not None and prix.isdigit():
                    obj = {
                        'nombre_pieces': nombre_pieces,
                        'prix': int(prix),
                        'adresse': adresse,
                        'image_lien': image_lien,
                        'source': lien_complet,
                        'date_scraping': date_scraping
                    }
                    data.append(obj)

            except Exception as e:
                continue

        df_page = pd.DataFrame(data)
        df = pd.concat([df, df_page], axis=0).reset_index(drop=True)

    return df


def dashboard_villas(df):
    st.subheader("📊 Dashboard - Villas")

    st.markdown("### 🔍 Aperçu des données")
    st.dataframe(df.head(10))

    st.markdown("### 📈 Répartition des prix")
    df['prix'] = pd.to_numeric(df['prix'], errors='coerce')
    fig, ax = plt.subplots()
    sns.histplot(df['prix'].dropna(), bins=30, kde=True, ax=ax)
    ax.set_xlabel("Prix (CFA)")
    st.pyplot(fig)

    st.markdown("### 📍 Top 10 des localités")
    st.bar_chart(df['adresse'].value_counts().head(10))

def dashboard_terrains(df):
    st.subheader("📊 Dashboard - Terrains")

    st.markdown("### 🔍 Aperçu des données")
    st.dataframe(df.head(10))

    df['prix'] = pd.to_numeric(df['prix'], errors='coerce')
    df['superficie'] = pd.to_numeric(df['superficie'], errors='coerce')

    st.markdown("### 📈 Répartition des prix")
    fig, ax = plt.subplots()
    sns.histplot(df['prix'].dropna(), bins=30, kde=True, ax=ax)
    ax.set_xlabel("Prix (CFA)")
    st.pyplot(fig)

    st.markdown("### 📐 Répartition des superficies")
    fig, ax = plt.subplots()
    sns.histplot(df['superficie'].dropna(), bins=30, kde=True, ax=ax)
    ax.set_xlabel("Superficie (m²)")
    st.pyplot(fig)

    st.markdown("### 📍 Top 10 des localités")
    st.bar_chart(df['adresse'].value_counts().head(10))

def dashboard_appartements(df):
    st.subheader("📊 Dashboard - Appartements")

    st.markdown("### 🔍 Aperçu des données")
    st.dataframe(df.head(10))

    df['prix'] = pd.to_numeric(df['prix'], errors='coerce')
    df['nombre_pieces'] = pd.to_numeric(df['nombre_pieces'], errors='coerce')

    st.markdown("### 📈 Répartition des prix")
    fig, ax = plt.subplots()
    sns.histplot(df['prix'].dropna(), bins=30, kde=True, ax=ax)
    ax.set_xlabel("Prix (CFA)")
    st.pyplot(fig)

    st.markdown("### 🛏 Nombre de pièces")
    fig, ax = plt.subplots()
    sns.countplot(x='nombre_pieces', data=df.dropna(subset=['nombre_pieces']), ax=ax)
    ax.set_xlabel("Nombre de pièces")
    st.pyplot(fig)

    st.markdown("### 📍 Top 10 des localités")
    st.bar_chart(df['adresse'].value_counts().head(10))

@st.cache_data
def scraper_villas():
    df = pd.DataFrame()

    for p in range(1, 50):  
        url = f'https://sn.coinafrique.com/categorie/villas?page={p}'
        res = get(url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all('div', class_='col s6 m4 l3')
        data = []

        for container in containers:
            try:
                lien_annonce = container.find('a', class_='card-image')['href']
                adresse = container.find('p', class_='ad__card-location').span.text.strip()

                # Scraping de la page de détails de l'annonce
                res_annonce = get("https://sn.coinafrique.com" + lien_annonce)
                soup_annonce = bs(res_annonce.text, 'html.parser')
                details = soup_annonce.find('div', class_='details-characteristics')

                pieces = bains = superficie = ''
                if details:
                    spans = details.find_all('span')
                    for i, span in enumerate(spans):
                        label = span.text.strip()
                        if label == "Nbre de pièces":
                            pieces = spans[i + 1].text.strip()
                        elif label == "Nbre de salles de bain":
                            bains = spans[i + 1].text.strip()
                        elif label == "Superficie":
                            superficie = spans[i + 1].text.strip()

                data.append({
                    'nombre_pieces': pieces,
                    'nombre_salle_bain': bains,
                    'superficie': superficie,
                    'adresse': adresse
                })

            except:
                continue

        df = pd.concat([df, pd.DataFrame(data)], axis=0).reset_index(drop=True)

    return df

def telecharger_villas():
    st.subheader("⬇️ Télécharger les données de villas (non nettoyées)")
    df = scraper_villas()
    st.write(df.head())
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Télécharger CSV Villas", csv, "villas.csv", "text/csv")

@st.cache_data
def scraper_terrains():
    df = pd.DataFrame()
    for p in range(1, 50):
        url = f'https://sn.coinafrique.com/categorie/terrains?page={p}'
        res = get(url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all('div', class_='col s6 m4 l3')
        data = []
        for container in containers:
            try:
                inf = container.find('p', class_='ad__card-description').text.split()
                superficie = inf[1]
                prix = container.find('p', class_='ad__card-price').text.replace(' ', '').replace('CFA', '')
                adresse = container.find('p', class_='ad__card-location').span.text
                image_lien = container.find('img', class_='ad__card-img')['src']
                obj = {
                    'superficie': superficie,
                    'prix': prix,
                    'adresse': adresse,
                    'image_lien': image_lien
                }
                data.append(obj)
            except:
                pass
        DF = pd.DataFrame(data)
        df = pd.concat([df, DF], axis=0).reset_index(drop=True)
    return df

def telecharger_terrains():
    st.subheader("⬇️ Télécharger les données de terrains (non nettoyées)")
    df = scraper_terrains()
    st.write(df.head())
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Télécharger CSV Terrains", csv, "terrains.csv", "text/csv")

@st.cache_data
def scraper_appartements():
    df = pd.DataFrame()

    for p in range(1, 50):  
        url = f'https://sn.coinafrique.com/categorie/appartements?page={p}'
        res = get(url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all('div', class_='col s6 m4 l3')
        data = []

        for container in containers:
            try:
                lien_annonce = container.find('a', class_='card-image')['href']
                adresse = container.find('p', class_='ad__card-location').span.text.strip()

                # Aller dans la page de l'annonce
                res_annonce = get("https://sn.coinafrique.com" + lien_annonce)
                soup_annonce = bs(res_annonce.text, 'html.parser')
                details = soup_annonce.find('div', class_='details-characteristics')

                pieces = bains = superficie = ''
                if details:
                    spans = details.find_all('span')
                    for i, span in enumerate(spans):
                        label = span.text.strip()
                        if label == "Nbre de pièces":
                            pieces = spans[i + 1].text.strip()
                        elif label == "Nbre de salles de bain":
                            bains = spans[i + 1].text.strip()
                        elif label == "Superficie":
                            superficie = spans[i + 1].text.strip()

                data.append({
                    'nombre_pieces': pieces,
                    'nombre_salle_bain': bains,
                    'superficie': superficie,
                    'adresse': adresse
                })

            except:
                continue

        df = pd.concat([df, pd.DataFrame(data)], axis=0).reset_index(drop=True)

    return df

def telecharger_appartements():
    st.subheader("⬇️ Télécharger les données d'appartements (non nettoyées)")
    df = scraper_appartements()
    st.write(df.head())
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Télécharger CSV Appartements", csv, "appartements.csv", "text/csv")


# --- Sidebar : paramètres globaux ---
st.sidebar.markdown("## Paramètres de scraping")

page_debut = st.sidebar.number_input("Page de début", min_value=1, max_value=100, value=1)
page_fin = st.sidebar.number_input("Page de fin", min_value=1, max_value=100, value=3)

st.sidebar.markdown("---")
menu_principal = st.sidebar.radio("Menu", [
    "Scraper avec BeautifulSoup",
    "Télécharger données Web Scraper",
    "Dashboard des données nettoyées",
    "Formulaire d’évaluation"
])

# Sous-menu uniquement pour les 3 premiers cas
if menu_principal in ["Scraper avec BeautifulSoup", "Télécharger données Web Scraper", "Dashboard des données nettoyées"]:
    sous_choix = st.sidebar.selectbox("Choisir une catégorie", ["Villas", "Terrains", "Appartements"])
else:
    sous_choix = None


# --- Corps de l'app en fonction du menu choisi ---
if menu_principal == "Scraper avec BeautifulSoup":
    st.header(f"🔍 Scraper des données (avec nettoyage) - {sous_choix}")
    st.info(f"Scraping des pages {page_debut} à {page_fin}")
    
    if sous_choix == "Villas":
        df = scrapper_villas(page_debut, page_fin)
    elif sous_choix == "Terrains":
        df = scrapper_terrains(page_debut, page_fin)
    elif sous_choix == "Appartements":
        df = scrapper_appartements(page_debut, page_fin)
    
    st.dataframe(df)

elif menu_principal == "Télécharger données Web Scraper":
    st.header(f"⬇️ Télécharger les données Web Scraper (non nettoyées) - {sous_choix}")
    
    if sous_choix == "Villas":
        df = scraper_villas()
    elif sous_choix == "Terrains":
        df = scraper_terrains()
    elif sous_choix == "Appartements":
        df = scraper_appartements()

    st.dataframe(df)
    st.download_button("📥 Télécharger CSV", data=df.to_csv(index=False), file_name=f"{sous_choix.lower()}_webscraped.csv", mime='text/csv')

elif menu_principal == "Dashboard des données nettoyées":
    st.header(f"📊 Dashboard - {sous_choix}")
    try:
        #df = pd.read_csv(f"{sous_choix.lower()}_cleaned.csv")

        if sous_choix == "Villas":
            df=scrapper_villas(page_debut,page_fin)
            dashboard_villas(df)
        elif sous_choix == "Terrains":
            df=scrapper_terrains(page_debut,page_fin)
            dashboard_terrains(df)
        elif sous_choix == "Appartements":
            df=scrapper_appartements(page_debut,page_fin)
            dashboard_appartements(df)

    except FileNotFoundError:
        st.error("Aucune donnée trouvée")



elif menu_principal == "Formulaire d’évaluation":
    st.header("📝 Formulaire d’évaluation")

    # Affichage du formulaire KoboCollect
    st.subheader("Formulaire KoboCollect")
    components.iframe("https://ee-eu.kobotoolbox.org/i/oN9qnekR",width=800,height=600)


