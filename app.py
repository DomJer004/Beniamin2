import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

st.set_page_config(page_title="Liga Mistrzów 25/26", layout="wide", page_icon="⚽")

EXCEL_FILE = "Liga Mistrzów 25_26.xlsx"

# --- 1. SŁOWNIKI I KONFIGURACJA ---

def normalize_key(name):
    """Czyści nazwę do formatu klucza (małe litery, bez spacji)."""
    if not isinstance(name, str): return ""
    return name.strip().lower()

# SŁOWNIK ALIASÓW (Aktualizacja o "Atlético Madyt")
TEAM_ALIASES = {
    "paris saint-germain": ["psg", "paris sg"],
    "psg": ["paris saint-germain", "paris sg"],
    "atlético madryt": ["atletico", "atlético", "atletico madrid", "atl. madryt", "atlético madyt", "atletico madyt"],
    "atletico": ["atlético madryt", "atletico madrid", "atlético madyt"],
    "union saint-gilloise": ["union sg", "usg", "union saint gilloise"],
    "bodø/glimt": ["bodo/glimt", "bodo glimt", "bodo"],
    "bodo/glimt": ["bodø/glimt"],
    "sporting cp": ["sporting", "sporting lizbona"],
    "sporting": ["sporting cp"],
    "inter mediolan": ["inter"],
    "inter": ["inter mediolan"],
    "ac milan": ["milan"],
    "milan": ["ac milan"],
    "bayer leverkusen": ["leverkusen", "bayer 04"],
    "rb leipzig": ["leipzig", "rbl"],
    "shakhtar donetsk": ["szachtar", "szachtar donieck"],
    "szachtar": ["shakhtar", "shakhtar donetsk"],
    "red star belgrade": ["crvena zvezda", "crvena"],
    "crvena zvezda": ["red star", "red star belgrade"]
}

def is_same_team(name1, name2):
    """Sprawdza czy dwie nazwy to ta sama drużyna (uwzględniając aliasy)."""
    n1 = normalize_key(name1)
    n2 = normalize_key(name2)
    
    if n1 == n2: return True
    if n1 in n2 or n2 in n1: return True
    
    # Sprawdzenie aliasów
    if n1 in TEAM_ALIASES:
        for alias in TEAM_ALIASES[n1]:
            if normalize_key(alias) == n2 or normalize_key(alias) in n2: return True
    
    if n2 in TEAM_ALIASES:
        for alias in TEAM_ALIASES[n2]:
            if normalize_key(alias) == n1 or normalize_key(alias) in n1: return True
            
    return False

# BAZA HERBÓW (Bez zmian)
CLUB_LOGOS_RAW = {
    "union saint-gilloise": "https://upload.wikimedia.org/wikipedia/en/6/64/Royale_Union_Saint-Gilloise_Logo.svg",
    "union sg": "https://upload.wikimedia.org/wikipedia/en/6/64/Royale_Union_Saint-Gilloise_Logo.svg",
    "usg": "https://upload.wikimedia.org/wikipedia/en/6/64/Royale_Union_Saint-Gilloise_Logo.svg",
    "paris saint-germain": "https://upload.wikimedia.org/wikipedia/en/a/a7/Paris_Saint-Germain_F.C..svg",
    "psg": "https://upload.wikimedia.org/wikipedia/en/a/a7/Paris_Saint-Germain_F.C..svg",
    "bodø/glimt": "https://upload.wikimedia.org/wikipedia/en/8/8d/FK_Bodo_Glimt_logo.svg",
    "bodo/glimt": "https://upload.wikimedia.org/wikipedia/en/8/8d/FK_Bodo_Glimt_logo.svg",
    "atlético madryt": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "atletico": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "monaco": "https://upload.wikimedia.org/wikipedia/fr/5/58/Logo_AS_Monaco_FC_-_2021.svg",
    "as monaco": "https://upload.wikimedia.org/wikipedia/fr/5/58/Logo_AS_Monaco_FC_-_2021.svg",
    "olympiacos": "https://upload.wikimedia.org/wikipedia/en/a/a2/Olympiacos_FC_crest.svg",
    "eintracht": "https://upload.wikimedia.org/wikipedia/en/7/7e/Eintracht_Frankfurt_crest.svg",
    "frankfurt": "https://upload.wikimedia.org/wikipedia/en/7/7e/Eintracht_Frankfurt_crest.svg",
    "kairat": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FCKairat_logo.png",
    "galatasaray": "https://upload.wikimedia.org/wikipedia/commons/2/20/Galatasaray_Sports_Club_Logo.svg",
    "karabach": "https://upload.wikimedia.org/wikipedia/az/1/13/Qaraba%C4%9F_FK_loqo.png",
    "qarabag": "https://upload.wikimedia.org/wikipedia/az/1/13/Qaraba%C4%9F_FK_loqo.png",
    "sporting": "https://upload.wikimedia.org/wikipedia/sco/3/3e/Sporting_Clube_de_Portugal.png",
    "sporting cp": "https://upload.wikimedia.org/wikipedia/sco/3/3e/Sporting_Clube_de_Portugal.png",
    "juventus": "https://upload.wikimedia.org/wikipedia/commons/e/ed/Juventus_FC_-_logo_black_%28Italy%2C_2020%29.svg",
    "juve": "https://upload.wikimedia.org/wikipedia/commons/e/ed/Juventus_FC_-_logo_black_%28Italy%2C_2020%29.svg",
    "pafos": "https://upload.wikimedia.org/wikipedia/en/9/9b/Pafos_FC_crest.svg",
    "villarreal": "https://upload.wikimedia.org/wikipedia/en/b/b9/Villarreal_CF_logo-en.svg",
    "slavia": "https://upload.wikimedia.org/wikipedia/commons/2/2b/SK_Slavia_Praha_full_logo.svg",
    "slavia praga": "https://upload.wikimedia.org/wikipedia/commons/2/2b/SK_Slavia_Praha_full_logo.svg",
    "kopenhaga": "https://upload.wikimedia.org/wikipedia/en/2/26/FC_Copenhagen_logo.svg",
    "fc kopenhaga": "https://upload.wikimedia.org/wikipedia/en/2/26/FC_Copenhagen_logo.svg",
    "ajax": "https://upload.wikimedia.org/wikipedia/en/7/79/Ajax_Amsterdam.svg",
    "arsenal": "https://upload.wikimedia.org/wikipedia/en/5/53/Arsenal_FC.svg",
    "aston villa": "https://upload.wikimedia.org/wikipedia/en/9/9f/Aston_Villa_logo.svg",
    "liverpool": "https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg",
    "manchester city": "https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
    "city": "https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
    "chelsea": "https://upload.wikimedia.org/wikipedia/en/c/cc/Chelsea_FC.svg",
    "tottenham": "https://upload.wikimedia.org/wikipedia/en/b/b4/Tottenham_Hotspur.svg",
    "newcastle": "https://upload.wikimedia.org/wikipedia/en/5/56/Newcastle_United_Logo.svg",
    "real madryt": "https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg",
    "real": "https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg",
    "barcelona": "https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg",
    "barca": "https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg",
    "girona": "https://upload.wikimedia.org/wikipedia/en/9/90/Girona_FC_Crest.svg",
    "bilbao": "https://upload.wikimedia.org/wikipedia/en/9/98/Club_Athletic_Bilbao_logo.svg",
    "bayern": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_München_logo_%282017%29.svg",
    "borussia": "https://upload.wikimedia.org/wikipedia/commons/6/67/Borussia_Dortmund_logo.svg",
    "leverkusen": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
    "leipzig": "https://upload.wikimedia.org/wikipedia/en/0/04/RB_Leipzig_2014_logo.svg",
    "stuttgart": "https://upload.wikimedia.org/wikipedia/commons/e/eb/VfB_Stuttgart_1893_Logo.svg",
    "inter": "https://upload.wikimedia.org/wikipedia/commons/0/05/FC_Internazionale_Milano_2021.svg",
    "milan": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Logo_of_AC_Milan.svg",
    "ac milan": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Logo_of_AC_Milan.svg",
    "atalanta": "https://upload.wikimedia.org/wikipedia/en/6/66/AtalantaBC.svg",
    "bologna": "https://upload.wikimedia.org/wikipedia/en/5/5b/Bologna_F.C._1909_logo.svg",
    "napoli": "https://upload.wikimedia.org/wikipedia/commons/2/2d/SSC_Neapel.svg",
    "brest": "https://upload.wikimedia.org/wikipedia/en/0/05/Stade_Brestois_29_logo.svg",
    "lille": "https://upload.wikimedia.org/wikipedia/en/6/6f/Lille_OSC_2018_logo.svg",
    "marsylia": "https://upload.wikimedia.org/wikipedia/commons/d/d8/Olympique_Marseille_logo.svg",
    "benfica": "https://upload.wikimedia.org/wikipedia/en/a/a2/SL_Benfica_logo.svg",
    "porto": "https://upload.wikimedia.org/wikipedia/en/f/f1/FC_Porto.svg",
    "psv": "https://upload.wikimedia.org/wikipedia/en/0/05/PSV_Eindhoven.svg",
    "feyenoord": "https://upload.wikimedia.org/wikipedia/en/e/e3/Feyenoord_logo.svg",
    "club brugge": "https://upload.wikimedia.org/wikipedia/en/d/d0/Club_Brugge_KV_logo.svg",
    "celtic": "https://upload.wikimedia.org/wikipedia/en/3/35/Celtic_FC.svg",
    "sturm": "https://upload.wikimedia.org/wikipedia/commons/c/cc/SK_Sturm_Graz_Logo.svg",
    "salzburg": "https://upload.wikimedia.org/wikipedia/en/7/77/FC_Red_Bull_Salzburg_logo.svg",
    "szachtar": "https://upload.wikimedia.org/wikipedia/en/a/a1/FC_Shakhtar_Donetsk.svg",
    "dinamo": "https://upload.wikimedia.org/wikipedia/en/f/f6/NK_Dinamo_Zagreb.svg",
    "crvena zvezda": "https://upload.wikimedia.org/wikipedia/commons/2/2a/Red_Star_Belgrade_logo.svg",
    "young boys": "https://upload.wikimedia.org/wikipedia/en/6/6b/BSC_Young_Boys_logo.svg",
    "sparta": "https://upload.wikimedia.org/wikipedia/en/3/39/AC_Sparta_Praha_logo.svg",
    "slovan": "https://upload.wikimedia.org/wikipedia/en/8/8b/Slovan_Bratislava_logo.svg"
}

# KOMPLETNA LISTA KODÓW FLAG
COUNTRY_CODES = {
    # Europa
    "anglia": "gb-eng", "szkocja": "gb-sct", "walia": "gb-wls", "polska": "pl", "hiszpania": "es", 
    "niemcy": "de", "włochy": "it", "francja": "fr", "portugalia": "pt", "holandia": "nl", 
    "belgia": "be", "chorwacja": "hr", "dania": "dk", "szwecja": "se", "norwegia": "no", 
    "irlandia": "ie", "czechy": "cz", "słowacja": "sk", "ukraina": "ua", "turcja": "tr", 
    "grecja": "gr", "szwajcaria": "ch", "austria": "at", "węgry": "hu", "rumunia": "ro", 
    "bułgaria": "bg", "serbia": "rs", "bośnia": "ba", "bośnia i hercegowina": "ba", 
    "cypr": "cy", "albania": "al", "słowenia": "si", "islandia": "is", "finlandia": "fi",
    "czarnogóra": "me", "macedonia": "mk", "macedonia północna": "mk", "kosowo": "xk",
    "mołdawia": "md", "białoruś": "by", "estonia": "ee", "litwa": "lt", "łotwa": "lv",
    "luksemburg": "lu", "malta": "mt", "rosja": "ru",
    
    # Ameryka Płd
    "brazylia": "br", "argentyna": "ar", "urugwaj": "uy", "kolumbia": "co", "chile": "cl",
    "ekwador": "ec", "paragwaj": "py", "wenezuela": "ve", "peru": "pe", "boliwia": "bo",
    
    # Ameryka Płn
    "usa": "us", "meksyk": "mx", "kanada": "ca", "jamajka": "jm", "kostaryka": "cr",
    "panama": "pa", "honduras": "hn", "surinam": "sr",
    
    # Azja
    "japonia": "jp", "korea": "kr", "korea południowa": "kr", "chiny": "cn", "iran": "ir",
    "izrael": "il", "gruzja": "ge", "armenia": "am", "azerbejdżan": "az", "kazachstan": "kz",
    "uzbekistan": "uz", "arabia saudyjska": "sa", "katar": "qa", "zjednoczone emiraty arabskie": "ae",
    "australia": "au",
    
    # Afryka
    "maroko": "ma", "senegal": "sn", "egipt": "eg", "wybrzeże kości słoniowej": "ci", "wks": "ci",
    "kamerun": "cm", "ghana": "gh", "nigeria": "ng", "algieria": "dz", "tunezja": "tn",
    "mali": "ml", "gwinea": "gn", "burkina faso": "bf", "gabon": "ga", "rpa": "za",
    "demokratyczna republika konga": "cd", "kongo": "cd"
}

def get_flag_html(nationality_str):
    """Generuje HTML z flagami."""
    if not isinstance(nationality_str, str) or not nationality_str.strip(): return ""
    
    parts = re.split(r'[,/]', nationality_str)
    html_out = ""
    
    for part in parts:
        clean_nat = normalize_key(part).strip()
        if not clean_nat: continue
        
        if "konaga" in clean_nat or "konga" in clean_nat: code = "cd"
        else:
            code = COUNTRY_CODES.get(clean_nat)
            if not code:
                for k, v in COUNTRY_CODES.items():
                    if k in clean_nat:
                        code = v
                        break
        
        if code:
            html_out += f'<img src="https://flagcdn.com/w40/{code}.png" width="22" style="margin-right:4px; vertical-align:middle; border:1px solid #ddd; border-radius:2px;">'
            
    return html_out

def get_club_logo_url(club_name):
    if not isinstance(club_name, str): return None
    key = normalize_key(club_name)
    if key in CLUB_LOGOS_RAW: return CLUB_LOGOS_RAW[key]
    for main_name, aliases in TEAM_ALIASES.items():
        if key == main_name or key in aliases:
            if main_name in CLUB_LOGOS_RAW: return CLUB_LOGOS_RAW[main_name]
    for k, v in CLUB_LOGOS_RAW.items():
        if k in key or key in k: return v
    return None

def get_club_logo_html(club_name):
    url = get_club_logo_url(club_name)
    if url: return f'<img src="{url}" width="25" style="vertical-align:middle;">'
    return club_name if club_name else ""

def repair_excel_date_score(value):
    if pd.isna(value): return None
    val_str = str(value).strip()
    try:
        dt = pd.to_datetime(value, errors='coerce')
        if not pd.isna(dt): return f"{dt.day}-{dt.month}"
    except: pass
    if "-" in val_str and len(val_str) < 8: return val_str
    return val_str

# --- 2. ŁADOWANIE DANYCH ---

@st.cache_data
def load_all_data(file_path):
    if not os.path.exists(file_path): return None
    try: return pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
    except: return None

def process_team_sheet(df, team_name):
    try:
        # Szukanie terminarza
        match_idx = -1
        for idx, row in df.iterrows():
            if row.astype(str).str.contains('kolejka', case=False).any():
                match_idx = idx; break
        if match_idx == -1: match_idx = len(df)
        
        df_top = df.iloc[:match_idx].copy()
        
        # Szukanie sztabu
        staff_idx = -1
        for idx, row in df_top.iterrows():
            if row.astype(str).str.contains('funkcja|rola', case=False, regex=True).any():
                staff_idx = idx; break
        
        if staff_idx != -1:
            df_players = df_top.loc[:staff_idx-1].copy()
            df_staff = df_top.loc[staff_idx:].copy()
            df_staff.columns = [str(c).lower().strip() for c in df_staff.iloc[0]]
            df_staff = df_staff[1:].dropna(subset=['funkcja']) if 'funkcja' in df_staff.columns else df_staff[1:]
        else:
            df_players = df_top.copy(); df_staff = pd.DataFrame()

        # Przetwarzanie graczy (Rozszerzone statystyki)
        if not df_players.empty:
            if isinstance(df_players.columns[0], int):
                df_players.columns = df_players.iloc[0].astype(str).str.lower().str.strip()
                df_players = df_players[1:]
            df_players.columns = [str(c).lower().strip() for c in df_players.columns]
            
            renames = {'t': 'numer', 'nr': 'numer', 'kraj': 'narodowość'}
            df_players.rename(columns=renames, inplace=True)
            
            if 'imię i nazwisko' in df_players.columns: 
                df_players = df_players.dropna(subset=['imię i nazwisko'])
            
            # Lista wszystkich statystyk do pobrania
            stats_cols = ['mecze', 'minuty', 'gole', 'asysty', 'żółte kartki', 'czerwone kartki', 
                          'czyste konta', 'kanadyjka', 'obronione karne', 'gole samobójcze', 'wiek']
            
            for col in stats_cols:
                if col in df_players.columns: 
                    # Konwersja na int, puste = 0
                    df_players[col] = pd.to_numeric(df_players[col], errors='coerce').fillna(0).astype(int)
            
            # Logika "Czyste konta tylko dla bramkarzy"
            # Jeśli kolumna 'pozycja' istnieje, czyścimy dane dla nie-bramkarzy
            if 'pozycja' in df_players.columns:
                is_gk = df_players['pozycja'].astype(str).str.lower().str.contains('br|gk|bramkarz')
                if 'czyste konta' in df_players.columns:
                    df_players.loc[~is_gk, 'czyste konta'] = 0 # Lub można ustawić na None/pusty string do wyświetlania
                if 'obronione karne' in df_players.columns:
                    df_players.loc[~is_gk, 'obronione karne'] = 0

            if 'narodowość' in df_players.columns:
                df_players['flaga_html'] = df_players['narodowość'].apply(get_flag_html)

        # Przetwarzanie meczów (Filtrowanie kolumn Info_X)
        df_matches = pd.DataFrame()
        if match_idx < len(df):
            header_row = df.iloc[match_idx]
            new_columns, indices = [], []
            seen = {}
            for i, c in enumerate(header_row):
                val = str(c).strip()
                col_name = f"Info_{i}" if pd.isna(c) or val == "" or val.lower() == "nan" else val
                seen[col_name] = seen.get(col_name, 0) + 1
                final = f"{col_name}_{seen[col_name]}" if seen[col_name] > 1 else col_name
                
                # FILTROWANIE KOLUMN "ŚMIECIOWYCH"
                if not final.startswith("Info_") and not final.startswith("Extra_"):
                    new_columns.append(final)
                    indices.append(i)
            
            df_matches = df.iloc[match_idx+1:, indices].copy()
            df_matches.columns = [str(c).lower().strip() for c in new_columns]
            if 'wynik' in df_matches.columns: df_matches['wynik'] = df_matches['wynik'].apply(repair_excel_date_score)

        return df_players, df_staff, df_matches
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- 3. AGREGACJA ---

def aggregate_matches(data_sheets, team_names):
    matches_dict = {}
    
    for team in team_names:
        _, _, df_m = process_team_sheet(data_sheets[team], team)
        if df_m.empty or 'wynik' not in df_m.columns: continue
        
        scorer_cols = [c for c in df_m.columns if any(x in str(c).lower() for x in ['gole', 'strzelcy', 'bramki', 'info', 'extra'])]
        
        for _, row in df_m.iterrows():
            h, g = str(row.get('gospodarze','')).strip(), str(row.get('goście','')).strip()
            # FIX: Czyszczenie kolejki, żeby uniknąć duplikatów "1" vs "1.0"
            raw_k = str(row.get('kolejka','0')).strip()
            if '.' in raw_k: raw_k = raw_k.split('.')[0]
            k = raw_k
            
            raw_res = str(row.get('wynik','')).strip()
            
            if not h or h.lower()=='nan' or not g: continue
            
            mid = "-".join(sorted([h, g])) + f"-k{k}"
            
            if mid not in matches_dict:
                matches_dict[mid] = {
                    "Kolejka": int(k) if k.isdigit() else 0,
                    "Gospodarze": h, "Goście": g, 
                    "Wynik": "-", "Excel_Res": None, 
                    "Strzelcy_H": [], "Strzelcy_A": []
                }
            
            if raw_res and raw_res.lower() != 'nan' and raw_res != '-' and matches_dict[mid]["Excel_Res"] is None:
                matches_dict[mid]["Excel_Res"] = raw_res

            is_home_sheet = is_same_team(team, h)
            is_away_sheet = is_same_team(team, g)
            
            found = []
            for sc in scorer_cols:
                if sc in row: # Sprawdź czy kolumna istnieje w tym wierszu
                    val = str(row[sc]).strip()
                    if val and val.lower() != 'nan' and len(val) > 2 and not val.isdigit():
                        for s in re.split(r'[,;]', val): 
                            if s.strip(): found.append(s.strip())
            
            target = matches_dict[mid]["Strzelcy_H"] if is_home_sheet else matches_dict[mid]["Strzelcy_A"] if is_away_sheet else None
            if target is not None:
                for s in found: target.append(s)

    for mid, data in matches_dict.items():
        ch, ca = len(data["Strzelcy_H"]), len(data["Strzelcy_A"])
        if ch > 0 or ca > 0:
            data["Wynik"] = f"{ch}-{ca}"
        elif data["Excel_Res"]:
            data["Wynik"] = data["Excel_Res"]
        else:
            data["Wynik"] = "-"
            
    return matches_dict

def calculate_table(matches_dict):
    stats = {}
    for data in matches_dict.values():
        h, g, res = data['Gospodarze'], data['Goście'], data['Wynik']
        for t in [h, g]:
            if t not in stats: stats[t] = {'M':0,'Pkt':0,'BZ':0,'BS':0,'W':0,'R':0,'P':0,'Dom_W':0,'Dom_R':0,'Dom_P':0,'Wyj_W':0,'Wyj_R':0,'Wyj_P':0,'Forma':[]}
        
        if '-' in res and res != '-':
            try:
                hg, ag = map(int, res.split('-'))
                stats[h]['M']+=1; stats[h]['BZ']+=hg; stats[h]['BS']+=ag
                stats[g]['M']+=1; stats[g]['BZ']+=ag; stats[g]['BS']+=hg
                
                if hg > ag:
                    stats[h]['Pkt']+=3; stats[h]['W']+=1; stats[h]['Dom_W']+=1; stats[h]['Forma'].append('W')
                    stats[g]['P']+=1; stats[g]['Wyj_P']+=1; stats[g]['Forma'].append('P')
                elif ag > hg:
                    stats[g]['Pkt']+=3; stats[g]['W']+=1; stats[g]['Wyj_W']+=1; stats[g]['Forma'].append('W')
                    stats[h]['P']+=1; stats[h]['Dom_P']+=1; stats[h]['Forma'].append('P')
                else:
                    stats[h]['Pkt']+=1; stats[h]['R']+=1; stats[h]['Dom_R']+=1; stats[h]['Forma'].append('R')
                    stats[g]['Pkt']+=1; stats[g]['R']+=1; stats[g]['Wyj_R']+=1; stats[g]['Forma'].append('R')
            except: pass
            
    rows = []
    for t, s in stats.items():
        rows.append({
            'klub': t, 'mecze': s['M'], 'punkty': s['Pkt'], 'strzelone': s['BZ'], 'stracone': s['BS'],
            'bilans': s['BZ']-s['BS'], 'wygrane': s['W'], 'remisy': s['R'], 'porażki': s['P'],
            'forma': "".join(s['Forma'][-5:]).replace("W","✅").replace("R","➖").replace("P","❌")
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(['punkty','bilans','strzelone'], ascending=[0,0,0]).reset_index(drop=True)
        df.index += 1; df['Miejsce'] = df.index
    return df

# --- 4. INTERFEJS ---

data_sheets = load_all_data(EXCEL_FILE)

if data_sheets:
    st.sidebar.title("Menu")
    sheet_names = list(data_sheets.keys())
    team_names = sorted([n for n in sheet_names if n not in ['Tabela', 'Strzelcy', 'Legenda', 'Info']])
    matches_dict = aggregate_matches(data_sheets, team_names)
    
    page = st.sidebar.radio("Wybierz widok", ["🏆 Tabela Ligowa", "📅 Terminarz", "🎯 Strzelcy", "⚽ Drużyny"])
    
    if page == "🏆 Tabela Ligowa":
        st.title("Tabela Ligi Mistrzów 25/26 (Live)")
        df = calculate_table(matches_dict)
        if not df.empty:
            df['logo_url'] = df['klub'].apply(get_club_logo_url)
            st.dataframe(df, use_container_width=True, hide_index=True, column_config={
                "logo_url": st.column_config.ImageColumn("Herb", width="small"),
                "bilans": st.column_config.ProgressColumn("Bilans", min_value=-20, max_value=50, format="%d"),
            }, column_order=['Miejsce','logo_url','klub','mecze','punkty','strzelone','stracone','bilans','wygrane','remisy','porażki','forma'])
        else: st.info("Brak danych.")

    elif page == "📅 Terminarz":
        st.title("Terminarz")
        df_sched = pd.DataFrame(list(matches_dict.values())).sort_values('Kolejka')
        if not df_sched.empty:
            rounds = sorted(df_sched['Kolejka'].unique())
            if rounds:
                sel = st.selectbox("Kolejka", rounds)
                for _, row in df_sched[df_sched['Kolejka']==sel].iterrows():
                    h, g, res = row['Gospodarze'], row['Goście'], row['Wynik']
                    with st.container():
                        c1, c2, c3, c4, c5 = st.columns([0.5, 3, 1, 3, 0.5])
                        with c1: 
                            if get_club_logo_url(h): st.image(get_club_logo_url(h), width=50)
                        with c2:
                            st.markdown(f"<div style='text-align:right; font-weight:bold'>{h}</div>", unsafe_allow_html=True)
                            if row['Strzelcy_H']: st.markdown(f"<div style='text-align:right; font-size:0.8em; color:gray'>⚽ {', '.join(row['Strzelcy_H'])}</div>", unsafe_allow_html=True)
                        with c3:
                            bg = "#a3ffa3" if res != "-" else "#e0e0e0"
                            st.markdown(f"<div style='background:{bg}; border-radius:5px; text-align:center; padding:5px; font-weight:bold'>{res}</div>", unsafe_allow_html=True)
                        with c4:
                            st.markdown(f"<div style='text-align:left; font-weight:bold'>{g}</div>", unsafe_allow_html=True)
                            if row['Strzelcy_A']: st.markdown(f"<div style='text-align:left; font-size:0.8em; color:gray'>⚽ {', '.join(row['Strzelcy_A'])}</div>", unsafe_allow_html=True)
                        with c5: 
                            if get_club_logo_url(g): st.image(get_club_logo_url(g), width=50)
                        st.divider()
            else: st.info("Brak kolejek.")

    elif page == "🎯 Strzelcy":
        st.title("Najlepsi Strzelcy")
        if 'Strzelcy' in data_sheets:
            df_s = data_sheets['Strzelcy']
            df_s.columns = [str(c).lower().strip() for c in df_s.columns]
            
            # 1. Narodowość (HTML)
            cols_to_keep = []
            if 'kraj' in df_s.columns:
                df_s['Narodowość'] = df_s['kraj'].apply(get_flag_html)
                cols_to_keep.append('Narodowość')
            elif 'narodowość' in df_s.columns:
                df_s['Narodowość'] = df_s['narodowość'].apply(get_flag_html)
                cols_to_keep.append('Narodowość')

            # 2. Klub (Logo HTML)
            club_col = next((c for c in df_s.columns if c in ['klub', 'zespół', 'drużyna', 'team']), None)
            if club_col:
                df_s['Klub'] = df_s[club_col].apply(get_club_logo_html)
                cols_to_keep.append('Klub')
            
            # 3. Reszta Danych (Int)
            ignored = ['kraj', 'narodowość', 'flaga_url', 'info', 'uwagi', club_col]
            data_cols = [c for c in df_s.columns if c not in ignored and c not in cols_to_keep]
            
            for col in data_cols:
                if pd.api.types.is_numeric_dtype(df_s[col]):
                    df_s[col] = df_s[col].fillna(0).astype(int)
            
            final_cols = cols_to_keep + data_cols
            
            st.markdown(df_s[final_cols].to_html(escape=False, index=False), unsafe_allow_html=True)
        else: st.warning("Brak arkusza Strzelcy.")

    elif page == "⚽ Drużyny":
        st.title("Profil Drużyny")
        sel = st.sidebar.selectbox("Klub", team_names)
        if sel:
            df_p, _, df_m = process_team_sheet(data_sheets[sel], sel)
            
            c1, c2 = st.columns([1, 5])
            with c1: 
                if get_club_logo_url(sel): st.image(get_club_logo_url(sel), width=100)
            with c2: st.header(sel)
            
            tab1, tab2, tab3 = st.tabs(["👥 Kadra", "📊 Statystyki", "📅 Mecze"])
            
            with tab1: # KADRA (Rozszerzona)
                if not df_p.empty:
                    # Lista kolumn w pożądanej kolejności
                    desired_order = ['numer', 'flaga_html', 'imię i nazwisko', 'pozycja', 'mecze', 'minuty', 'gole', 'asysty', 
                                     'żółte kartki', 'czerwone kartki', 'czyste konta', 'obronione karne', 'kanadyjka']
                    
                    final_cols = [c for c in desired_order if c in df_p.columns]
                    
                    disp = df_p[final_cols].rename(columns={'flaga_html': 'Narodowość', 'numer': '#'})
                    
                    # Warunkowe formatowanie dla BR (można to zrobić w HTML)
                    # Tutaj po prostu wyświetlamy
                    st.markdown(disp.to_html(escape=False, index=False), unsafe_allow_html=True)
            
            with tab2:
                if not df_p.empty and 'gole' in df_p.columns:
                    sc = df_p[df_p['gole']>0].sort_values('gole')
                    if not sc.empty: st.plotly_chart(px.bar(sc, x='gole', y='imię i nazwisko', orientation='h', title="Strzelcy"), use_container_width=True)
            
            with tab3:
                if not df_m.empty: st.dataframe(df_m, use_container_width=True, hide_index=True)
else:
    st.error(f"Nie znaleziono {EXCEL_FILE}")
