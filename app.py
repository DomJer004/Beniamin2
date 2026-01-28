import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Konfiguracja strony
st.set_page_config(page_title="Liga Mistrzów 25/26", layout="wide", page_icon="⚽")

# Stała nazwa pliku Excel
EXCEL_FILE = "Liga Mistrzów 25_26.xlsx"

# --- BAZA FLAG (Zabezpieczenie) ---
FLAG_MAP = {
    "Polska": "🇵🇱", "Hiszpania": "🇪🇸", "Niemcy": "🇩🇪", "Anglia": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Włochy": "🇮🇹", "Francja": "🇫🇷", "Portugalia": "🇵🇹", "Holandia": "🇳🇱",
    "Brazylia": "🇧🇷", "Argentyna": "🇦🇷", "Urugwaj": "🇺🇾", "Belgia": "🇧🇪",
    "Chorwacja": "🇭🇷", "Dania": "🇩🇰", "Szwecja": "🇸🇪", "Norwegia": "🇳🇴",
    "Szkocja": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Walia": "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "Irlandia": "🇮🇪", "Czechy": "🇨🇿",
    "Słowacja": "🇸🇰", "Ukraina": "🇺🇦", "Turcja": "🇹🇷", "Grecja": "🇬🇷",
    "USA": "🇺🇸", "Kanada": "🇨🇦", "Meksyk": "🇲🇽", "Kolumbia": "🇨🇴",
    "Chile": "🇨🇱", "Japonia": "🇯🇵", "Korea Południowa": "🇰🇷", "Chiny": "🇨🇳",
    "Maroko": "🇲🇦", "Senegal": "🇸🇳", "Egipt": "🇪🇬", "Nigeria": "🇳🇬",
    "Kamerun": "🇨🇲", "Ghana": "🇬🇭", "Wybrzeże Kości Słoniowej": "🇨🇮",
    "Algieria": "🇩🇿", "Tunezja": "🇹🇳", "Australia": "🇦🇺", "Austria": "🇦🇹",
    "Szwajcaria": "🇨🇭", "Serbia": "🇷🇸", "Bośnia i Hercegowina": "🇧🇦",
    "Węgry": "🇭🇺", "Rumunia": "🇷🇴", "Bułgaria": "🇧🇬", "Finlandia": "🇫🇮",
    "Islandia": "🇮🇸", "Słowenia": "🇸🇮", "Gruzja": "🇬🇪", "Armenia": "🇦🇲",
    "Azerbejdżan": "🇦🇿", "Kazachstan": "🇰🇿", "Izrael": "🇮🇱", "Cypr": "🇨🇾",
    "Gwinea": "🇬🇳", "Gwinea Równikowa": "🇬🇶", "Mali": "🇲🇱", "Gabon": "🇬🇦",
    "Gambia": "🇬🇲", "Kongo": "🇨🇩", "Ekwador": "🇪🇨", "Paragwaj": "🇵🇾",
    "Wenezuela": "🇻🇪", "Peru": "🇵🇪", "Albania": "🇦🇱", "Kosowo": "🇽🇰",
    "Czarnogóra": "🇲🇪", "Macedonia Północna": "🇲🇰", "Iran": "🇮🇷"
}

def get_flag_fallback(nationality_str):
    if not isinstance(nationality_str, str):
        return ""
    parts = nationality_str.replace("/", ",").split(",")
    flags = []
    for part in parts:
        country = part.strip()
        flag = FLAG_MAP.get(country, "")
        if flag:
            flags.append(flag)
    return " ".join(flags) if flags else ""

# --- FUNKCJE ŁADOWANIA DANYCH ---

@st.cache_data
def load_all_data(file_path):
    if not os.path.exists(file_path):
        st.error(f"❌ Nie znaleziono pliku: {file_path}")
        return None
    try:
        all_sheets = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
        return all_sheets
    except Exception as e:
        st.error(f"❌ Błąd odczytu Excela: {e}")
        return None

def clean_matches_table(df, start_row_idx):
    header_row = df.iloc[start_row_idx]