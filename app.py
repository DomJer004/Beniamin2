import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Konfiguracja strony
st.set_page_config(page_title="Liga Mistrzów 25/26", layout="wide", page_icon="⚽")

# Stała nazwa pliku Excel
EXCEL_FILE = "Liga Mistrzów 25_26.xlsx"

# --- BAZA FLAG ---
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
    new_columns = []
    indices_to_keep = []
    seen_cols = {}
    
    for i, col_name in enumerate(header_row):
        if pd.isna(col_name) or str(col_name).strip() == "" or str(col_name).lower() == "nan":
            continue
        col_str = str(col_name).strip()
        if col_str in seen_cols:
            seen_cols[col_str] += 1
            final_name = f"{col_str}_{seen_cols[col_str]}"
        else:
            seen_cols[col_str] = 1
            final_name = col_str
        new_columns.append(final_name)
        indices_to_keep.append(i)
    
    df_matches = df.iloc[start_row_idx+1:, indices_to_keep].copy()
    df_matches.columns = new_columns
    if 'kolejka' in df_matches.columns:
        df_matches = df_matches.dropna(subset=['kolejka'])
    return df_matches

def process_team_sheet(df, team_name):
    try:
        split_indices = df.index[df.iloc[:, 0].astype(str).str.lower() == 'kolejka'].tolist()
        
        if split_indices:
            idx = split_indices[0]
            
            # --- ZAWODNICY ---
            df_players = df.iloc[:idx].copy()
            df_players = df_players.dropna(how='all')
            df_players.columns = [str(c).lower().strip() for c in df_players.columns]
            df_players.rename(columns={'t': 'numer', 'nr': 'numer'}, inplace=True)
            
            # Konwersja liczb
            cols_to_numeric = ['mecze', 'minuty', 'gole', 'asysty', 'żółte kartki', 'kanadyjka', 'wiek']
            for col in cols_to_numeric:
                if col in df_players.columns:
                    df_players[col] = pd.to_numeric(df_players[col], errors='coerce').fillna(0).astype(int)

            # --- LOGIKA FLAG ---
            def resolve_flag(row):
                excel_flag = str(row['flaga']) if 'flaga' in row else ""
                nation = str(row['narodowość']) if 'narodowość' in row else ""
                
                if excel_flag.lower() in ['nan', '#ref!', 'nat', '', 'none']:
                    generated_flag = get_flag_fallback(nation)
                    return f"{generated_flag} {nation}".strip()
                else:
                    return f"{excel_flag} {nation}".strip()

            if 'narodowość' in df_players.columns:
                df_players['kraj'] = df_players.apply(resolve_flag, axis=1)
            else:
                df_players['kraj'] = ""

            # --- MECZE ---
            df_matches = clean_matches_table(df, idx)
            return df_players, df_matches
        else:
            return df, pd.DataFrame()
    except Exception as e:
        st.warning(f"⚠️ Problem z zakładką '{team_name}': {e}")
        return pd.DataFrame(), pd.DataFrame()

# --- START APLIKACJI ---

data_sheets = load_all_data(EXCEL_FILE)

if data_sheets:
    st.sidebar.title("Menu")
    sheet_names = list(data_sheets.keys())
    special_sheets = ['Tabela', 'Strzelcy', 'Legenda', 'Info']
    team_names = sorted([n for n in sheet_names if n not
