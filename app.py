import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

st.set_page_config(page_title="Liga Mistrzów 25/26", layout="wide", page_icon="⚽")

EXCEL_FILE = "Liga Mistrzów 25_26.xlsx"

# --- 1. CONFIG & SŁOWNIKI ---

def normalize_key(name):
    """Czyści nazwę do formatu klucza (małe litery, bez spacji)."""
    if not isinstance(name, str): return ""
    return name.strip().lower()

# BAZA HERBÓW - KOMPLETNA
CLUB_LOGOS_RAW = {
    # --- TWOJE LINKI (ZAKTUALIZOWANE) ---
    "monaco": "https://upload.wikimedia.org/wikipedia/fr/5/58/Logo_AS_Monaco_FC_-_2021.svg",
    "as monaco": "https://upload.wikimedia.org/wikipedia/fr/5/58/Logo_AS_Monaco_FC_-_2021.svg",
    "olympiacos": "https://upload.wikimedia.org/wikipedia/en/a/a2/Olympiacos_FC_crest.svg",
    "olympiakos": "https://upload.wikimedia.org/wikipedia/en/a/a2/Olympiacos_FC_crest.svg",
    "eintracht": "https://upload.wikimedia.org/wikipedia/en/7/7e/Eintracht_Frankfurt_crest.svg",
    "frankfurt": "https://upload.wikimedia.org/wikipedia/en/7/7e/Eintracht_Frankfurt_crest.svg",
    "kairat": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FCKairat_logo.png",
    "kairat ałmaty": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FCKairat_logo.png",
    "galatasaray": "https://upload.wikimedia.org/wikipedia/commons/2/20/Galatasaray_Sports_Club_Logo.svg",
    "karabach": "https://upload.wikimedia.org/wikipedia/az/1/13/Qaraba%C4%9F_FK_loqo.png",
    "qarabag": "https://upload.wikimedia.org/wikipedia/az/1/13/Qaraba%C4%9F_FK_loqo.png",
    "sporting": "https://upload.wikimedia.org/wikipedia/sco/3/3e/Sporting_Clube_de_Portugal.png",
    "sporting cp": "https://upload.wikimedia.org/wikipedia/sco/3/3e/Sporting_Clube_de_Portugal.png",
    "juventus": "https://upload.wikimedia.org/wikipedia/commons/e/ed/Juventus_FC_-_logo_black_%28Italy%2C_2020%29.svg",
    "juve": "https://upload.wikimedia.org/wikipedia/commons/e/ed/Juventus_FC_-_logo_black_%28Italy%2C_2020%29.svg",
    "pafos": "https://upload.wikimedia.org/wikipedia/en/9/9b/Pafos_FC_crest.svg",
    "bodo": "https://upload.wikimedia.org/wikipedia/en/8/8d/FK_Bodo_Glimt_logo.svg",
    "bodo/glimt": "https://upload.wikimedia.org/wikipedia/en/8/8d/FK_Bodo_Glimt_logo.svg",
    "villarreal": "https://upload.wikimedia.org/wikipedia/en/b/b9/Villarreal_CF_logo-en.svg",
    "slavia": "https://upload.wikimedia.org/wikipedia/commons/2/2b/SK_Slavia_Praha_full_logo.svg",
    "slavia praga": "https://upload.wikimedia.org/wikipedia/commons/2/2b/SK_Slavia_Praha_full_logo.svg",
    "kopenhaga": "https://upload.wikimedia.org/wikipedia/en/2/26/FC_Copenhagen_logo.svg",
    "fc kopenhaga": "https://upload.wikimedia.org/wikipedia/en/2/26/FC_Copenhagen_logo.svg",
    "ajax": "https://upload.wikimedia.org/wikipedia/en/7/79/Ajax_Amsterdam.svg",

    # --- ANGLIA ---
    "arsenal": "https://upload.wikimedia.org/wikipedia/en/5/53/Arsenal_FC.svg",
    "aston villa": "https://upload.wikimedia.org/wikipedia/en/9/9f/Aston_Villa_logo.svg",
    "liverpool": "https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg",
    "manchester city": "https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
    "city": "https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
    "chelsea": "https://upload.wikimedia.org/wikipedia/en/c/cc/Chelsea_FC.svg",
    "tottenham": "https://upload.wikimedia.org/wikipedia/en/b/b4/Tottenham_Hotspur.svg",
    "newcastle": "https://upload.wikimedia.org/wikipedia/en/5/56/Newcastle_United_Logo.svg",
    
    # --- HISZPANIA ---
    "real madryt": "https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg",
    "real": "https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg",
    "barcelona": "https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg",
    "barca": "https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg",
    "atletico": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "atletico madryt": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "girona": "https://upload.wikimedia.org/wikipedia/en/9/90/Girona_FC_Crest.svg",
    "bilbao": "https://upload.wikimedia.org/wikipedia/en/9/98/Club_Athletic_Bilbao_logo.svg",
    "athletic bilbao": "https://upload.wikimedia.org/wikipedia/en/9/98/Club_Athletic_Bilbao_logo.svg",
    
    # --- NIEMCY ---
    "bayern": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_München_logo_%282017%29.svg",
    "bayern monachium": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_München_logo_%282017%29.svg",
    "borussia": "https://upload.wikimedia.org/wikipedia/commons/6/67/Borussia_Dortmund_logo.svg",
    "borussia dortmund": "https://upload.wikimedia.org/wikipedia/commons/6/67/Borussia_Dortmund_logo.svg",
    "leverkusen": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
    "bayer leverkusen": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
    "leipzig": "https://upload.wikimedia.org/wikipedia/en/0/04/RB_Leipzig_2014_logo.svg",
    "rb leipzig": "https://upload.wikimedia.org/wikipedia/en/0/04/RB_Leipzig_2014_logo.svg",
    "stuttgart": "https://upload.wikimedia.org/wikipedia/commons/e/eb/VfB_Stuttgart_1893_Logo.svg",
    
    # --- WŁOCHY ---
    "inter": "https://upload.wikimedia.org/wikipedia/commons/0/05/FC_Internazionale_Milano_2021.svg",
    "inter mediolan": "https://upload.wikimedia.org/wikipedia/commons/0/05/FC_Internazionale_Milano_2021.svg",
    "milan": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Logo_of_AC_Milan.svg",
    "ac milan": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Logo_of_AC_Milan.svg",
    "atalanta": "https://upload.wikimedia.org/wikipedia/en/6/66/AtalantaBC.svg",
    "bologna": "https://upload.wikimedia.org/wikipedia/en/5/5b/Bologna_F.C._1909_logo.svg",
    "napoli": "https://upload.wikimedia.org/wikipedia/commons/2/2d/SSC_Neapel.svg",
    
    # --- FRANCJA ---
    "psg": "https://upload.wikimedia.org/wikipedia/en/a/a7/Paris_Saint-Germain_F.C..svg",
    "brest": "https://upload.wikimedia.org/wikipedia/en/0/05/Stade_Brestois_29_logo.svg",
    "lille": "https://upload.wikimedia.org/wikipedia/en/6/6f/Lille_OSC_2018_logo.svg",
    "marsylia": "https://upload.wikimedia.org/wikipedia/commons/d/d8/Olympique_Marseille_logo.svg",
    
    # --- POZOSTAŁE ---
    "benfica": "https://upload.wikimedia.org/wikipedia/en/a/a2/SL_Benfica_logo.svg",
    "porto": "https://upload.wikimedia.org/wikipedia/en/f/f1/FC_Porto.svg",
    "fc porto": "https://upload.wikimedia.org/wikipedia/en/f/f1/FC_Porto.svg",
    "psv": "https://upload.wikimedia.org/wikipedia/en/0/05/PSV_Eindhoven.svg",
    "psv eindhoven": "https://upload.wikimedia.org/wikipedia/en/0/05/PSV_Eindhoven.svg",
    "feyenoord": "https://upload.wikimedia.org/wikipedia/en/e/e3/Feyenoord_logo.svg",
    "club brugge": "https://upload.wikimedia.org/wikipedia/en/d/d0/Club_Brugge_KV_logo.svg",
    "brugge": "https://upload.wikimedia.org/wikipedia/en/d/d0/Club_Brugge_KV_logo.svg",
    "celtic": "https://upload.wikimedia.org/wikipedia/en/3/35/Celtic_FC.svg",
    "sturm": "https://upload.wikimedia.org/wikipedia/commons/c/cc/SK_Sturm_Graz_Logo.svg",
    "sturm graz": "https://upload.wikimedia.org/wikipedia/commons/c/cc/SK_Sturm_Graz_Logo.svg",
    "salzburg": "https://upload.wikimedia.org/wikipedia/en/7/77/FC_Red_Bull_Salzburg_logo.svg",
    "rb salzburg": "https://upload.wikimedia.org/wikipedia/en/7/77/FC_Red_Bull_Salzburg_logo.svg",
    "szachtar": "https://upload.wikimedia.org/wikipedia/en/a/a1/FC_Shakhtar_Donetsk.svg",
    "szachtar donieck": "https://upload.wikimedia.org/wikipedia/en/a/a1/FC_Shakhtar_Donetsk.svg",
    "dinamo": "https://upload.wikimedia.org/wikipedia/en/f/f6/NK_Dinamo_Zagreb.svg",
    "dinamo zagrzeb": "https://upload.wikimedia.org/wikipedia/en/f/f6/NK_Dinamo_Zagreb.svg",
    "crvena zvezda": "https://upload.wikimedia.org/wikipedia/commons/2/2a/Red_Star_Belgrade_logo.svg",
    "young boys": "https://upload.wikimedia.org/wikipedia/en/6/6b/BSC_Young_Boys_logo.svg",
    "sparta": "https://upload.wikimedia.org/wikipedia/en/3/39/AC_Sparta_Praha_logo.svg",
    "sparta praga": "https://upload.wikimedia.org/wikipedia/en/3/39/AC_Sparta_Praha_logo.svg",
    "slovan": "https://upload.wikimedia.org/wikipedia/en/8/8b/Slovan_Bratislava_logo.svg",
    "slovan bratysława": "https://upload.wikimedia.org/wikipedia/en/8/8b/Slovan_Bratislava_logo.svg"
}

COUNTRY_CODES = {
    "anglia": "gb-eng", "szkocja": "gb-sct", "walia": "gb-wls", "polska": "pl", "hiszpania": "es", 
    "niemcy": "de", "włochy": "it", "francja": "fr", "portugalia": "pt", "holandia": "nl", 
    "belgia": "be", "chorwacja": "hr", "dania": "dk", "szwecja": "se", "norwegia": "no", 
    "irlandia": "ie", "czechy": "cz", "słowacja": "sk", "ukraina": "ua", "turcja": "tr", 
    "grecja": "gr", "szwajcaria": "ch", "austria": "at", "węgry": "hu", "rumunia": "ro", 
    "bułgaria": "bg", "serbia": "rs", "bośnia": "ba", "brazylia": "br", "argentyna": "ar", 
    "urugwaj": "uy", "kolumbia": "co", "usa": "us", "meksyk": "mx", "japonia": "jp", 
    "korea": "kr", "kanada": "ca", "maroko": "ma", "senegal": "sn", "egipt": "eg",
    "wybrzeże kości słoniowej": "ci", "wks": "ci", "kamerun": "cm", "ghana": "gh", "nigeria": "ng",
    "algieria": "dz", "tunezja": "tn", "mali": "ml", "iran": "ir", "izrael": "il", "gruzja": "ge",
    "armenia": "am", "azerbejdżan": "az", "kazachstan": "kz", "cypr": "cy", "albania": "al"
}

def get_flag_url(nationality_str):
    if not isinstance(nationality_str, str) or not nationality_str.strip(): return None
    # Dzielenie "Anglia / Irlandia" -> bierze "Anglia"
    clean_nat = normalize_key(nationality_str).replace("/", ",").split(",")[0].strip()
    
    if "konaga" in clean_nat or "konga" in clean_nat: return "https://flagcdn.com/w40/cd.png"
    
    code = COUNTRY_CODES.get(clean_nat)
    # Fallback partial match
    if not code:
        for k, v in COUNTRY_CODES.items():
            if k in clean_nat:
                code = v
                break
    return f"https://flagcdn.com/w40/{code}.png" if code else None

def get_club_logo_url(club_name):
    if not isinstance(club_name, str): return None
    key = normalize_key(club_name)
    # Najpierw exact match
    if key in CLUB_LOGOS_RAW:
        return CLUB_LOGOS_RAW[key]
    # Potem partial match (np. "real madryt cf" -> "real madryt")
    for k, v in CLUB_LOGOS_RAW.items():
        if k in key or key in k:
            return v
    return None

def repair_excel_date_score(value):
    if pd.isna(value): return None
    val_str = str(value).strip()
    try:
        dt = pd.to_datetime(value, errors='coerce')
        if not pd.isna(dt):
            return f"{dt.day}-{dt.month}"
    except:
        pass
    if "-" in val_str and len(val_str) < 8:
        return val_str
    return val_str

# --- 2. ŁADOWANIE DANYCH ---

@st.cache_data
def load_all_data(file_path):
    if not os.path.exists(file_path): return None
    try: return pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
    except: return None

def clean_matches_table(df, start_row_idx):
    header_row = df.iloc[start_row_idx]
    new_columns, indices = [], []
    seen = {}
    
    for i, c in enumerate(header_row):
        val = str(c).strip()
        if pd.isna(c) or val == "" or val.lower() == "nan": 
            col_name = f"Info_{i}"
        else:
            col_name = val
            
        seen[col_name] = seen.get(col_name, 0) + 1
        final_name = f"{col_name}_{seen[col_name]}" if seen[col_name] > 1 else col_name
        new_columns.append(final_name)
        indices.append(i)
    
    matches = df.iloc[start_row_idx+1:, indices].copy()
    matches.columns = [str(c).lower().strip() for c in new_columns]
    
    if 'wynik' in matches.columns:
        matches['wynik'] = matches['wynik'].apply(repair_excel_date_score)
        
    return matches

def process_team_sheet(df, team_name):
    try:
        match_idx = -1
        for idx, row in df.iterrows():
            if row.astype(str).str.contains('kolejka', case=False).any():
                match_idx = idx
                break
        
        if match_idx == -1: match_idx = len(df)
        df_top = df.iloc[:match_idx].copy()
        
        staff_idx = -1
        for idx, row in df_top.iterrows():
            row_str = row.astype(str).str.lower()
            if row_str.str.contains('funkcja').any() or row_str.str.contains('rola').any():
                staff_idx = idx
                break
        
        if staff_idx != -1:
            df_players = df_top.loc[:staff_idx-1].copy()
            df_staff_raw = df_top.loc[staff_idx:]
            new_header = df_staff_raw.iloc[0]
            df_staff = df_staff_raw[1:].copy()
            df_staff.columns = [str(c).lower().strip() for c in new_header]
            if 'rola' in df_staff.columns: df_staff.rename(columns={'rola': 'funkcja'}, inplace=True)
            df_staff = df_staff.dropna(subset=['funkcja'])
        else:
            df_players = df_top.copy()
            df_staff = pd.DataFrame()

        if not df_players.empty:
            if isinstance(df_players.columns[0], int):
                df_players.columns = df_players.iloc[0].astype(str).str.lower().str.strip()
                df_players = df_players[1:]
            
            df_players.columns = [str(c).lower().strip() for c in df_players.columns]
            df_players.rename(columns={'t': 'numer', 'nr': 'numer'}, inplace=True)
            if 'imię i nazwisko' in df_players.columns:
                df_players = df_players.dropna(subset=['imię i nazwisko'])
            
            cols_num = ['mecze', 'minuty', 'gole', 'asysty', 'żółte kartki', 'kanadyjka', 'wiek']
            for col in cols_num:
                if col in df_players.columns:
                    df_players[col] = pd.to_numeric(df_players[col], errors='coerce').fillna(0).astype(int)
            
            if 'narodowość' in df_players.columns:
                df_players['flaga_url'] = df_players['narodowość'].apply(get_flag_url)

        if not df_staff.empty and 'narodowość' in df_staff.columns:
            df_staff['flaga_url'] = df_staff['narodowość'].apply(get_flag_url)

        df_matches = pd.DataFrame()
        if match_idx < len(df):
            df_matches = clean_matches_table(df, match_idx)

        return df_players, df_staff, df_matches
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- 3. AGREGACJA MECZÓW I LICZENIE WYNIKÓW Z GOLI ---

def aggregate_matches(data_sheets, team_names):
    matches_dict = {}
    
    for team in team_names:
        _, _, df_m = process_team_sheet(data_sheets[team], team)
        
        if not df_m.empty and 'wynik' in df_m.columns:
            # Szukamy kolumn, które mogą zawierać strzelców
            scorer_cols = [c for c in df_m.columns if any(x in str(c).lower() for x in ['gole', 'strzelcy', 'bramki', 'info', 'extra'])]
            
            for _, row in df_m.iterrows():
                h = str(row.get('gospodarze', '')).strip()
                g = str(row.get('goście', '')).strip()
                k = str(row.get('kolejka', '0')).strip()
                
                if not h or h.lower()=='nan' or not g: continue
                match_id = "-".join(sorted([h, g])) + f"-k{k}"
                
                if match_id not in matches_dict:
                    matches_dict[match_id] = {
                        "Kolejka": int(k) if k.isdigit() else 0,
                        "Gospodarze": h, "Goście": g, "Wynik": "-",
                        "Strzelcy_H": [], "Strzelcy_A": []
                    }
                
                is_home = (normalize_key(team) == normalize_key(h) or normalize_key(team) in normalize_key(h))
                is_away = (normalize_key(team) == normalize_key(g) or normalize_key(team) in normalize_key(g))
                
                # Zbieranie strzelców (rozdzielanie po przecinku)
                found_scorers = []
                for sc in scorer_cols:
                    val = str(row[sc]).strip()
                    if val and val.lower() != 'nan' and len(val) > 2 and not val.isdigit():
                        # Obsługa "Kane, Saka" w jednej komórce
                        for single_scorer in val.split(','):
                            clean_scorer = single_scorer.strip()
                            if clean_scorer:
                                found_scorers.append(clean_scorer)
                
                if found_scorers:
                    target_list = matches_dict[match_id]["Strzelcy_H"] if is_home else matches_dict[match_id]["Strzelcy_A"] if is_away else None
                    if target_list is not None:
                        # Unikaj duplikatów tylko jeśli ten sam arkusz jest czytany wielokrotnie
                        # Tutaj czytamy każdy arkusz raz, więc appendujemy
                        # Ale musimy uważać, by nie dodać tych samych strzelców z arkusza przeciwnika
                        # Przyjęcie strategii: Arkusz drużyny X podaje strzelców TYLKO drużyny X.
                        # (Większość arkuszy ma kolumny "Gole dla nas" i "Gole dla nich", tu zakładamy, że czytamy "Dla nas")
                        # Prosta heurystyka: Dodajemy wszystkich znalezionych w arkuszu.
                        # Ulepszenie: Sprawdźmy czy nie dublujemy (set)
                         for s in found_scorers:
                            if s not in target_list:
                                target_list.append(s)

    # OBLICZANIE WYNIKU NA PODSTAWIE LICZBY STRZELCÓW
    for mid, data in matches_dict.items():
        count_h = len(data["Strzelcy_H"])
        count_a = len(data["Strzelcy_A"])
        
        # Jeśli są jacyś strzelcy, wynik to liczba strzelców
        if count_h > 0 or count_a > 0:
            data["Wynik"] = f"{count_h}-{count_a}"
        else:
            # Jeśli brak strzelców, spróbuj zachować wynik z Excela (jeśli był wczytany, tu domyślnie "-")
            pass 

    return matches_dict

def calculate_table_from_matches(matches_dict):
    stats = {}
    
    for mid, data in matches_dict.items():
        h, g = data['Gospodarze'], data['Goście']
        res = data['Wynik']
        
        for t in [h, g]:
            if t not in stats: stats[t] = {
                'M':0, 'Pkt':0, 'BZ':0, 'BS':0, 'W':0, 'R':0, 'P':0, 
                'Dom_M':0, 'Dom_W':0, 'Dom_R':0, 'Dom_P':0,
                'Wyj_M':0, 'Wyj_W':0, 'Wyj_R':0, 'Wyj_P':0, 'Forma': []
            }

        if '-' in res and res != "-":
            try:
                hg, ag = map(int, res.split('-'))
                stats[h]['M'] += 1; stats[h]['BZ'] += hg; stats[h]['BS'] += ag; stats[h]['Dom_M'] += 1
                stats[g]['M'] += 1; stats[g]['BZ'] += ag; stats[g]['BS'] += hg; stats[g]['Wyj_M'] += 1
                
                if hg > ag:
                    stats[h]['Pkt'] += 3; stats[h]['W'] += 1; stats[h]['Dom_W'] += 1; stats[h]['Forma'].append('W')
                    stats[g]['P'] += 1; stats[g]['Wyj_P'] += 1; stats[g]['Forma'].append('P')
                elif ag > hg:
                    stats[g]['Pkt'] += 3; stats[g]['W'] += 1; stats[g]['Wyj_W'] += 1; stats[g]['Forma'].append('W')
                    stats[h]['P'] += 1; stats[h]['Dom_P'] += 1; stats[h]['Forma'].append('P')
                else:
                    stats[h]['Pkt'] += 1; stats[h]['R'] += 1; stats[h]['Dom_R'] += 1; stats[h]['Forma'].append('R')
                    stats[g]['Pkt'] += 1; stats[g]['R'] += 1; stats[g]['Wyj_R'] += 1; stats[g]['Forma'].append('R')
            except: pass

    table_data = []
    for team, s in stats.items():
        forma = "".join(s['Forma'][-5:]).replace("W", "✅").replace("R", "➖").replace("P", "❌")
        table_data.append({
            'klub': team, 'mecze': s['M'], 'punkty': s['Pkt'], 'strzelone': s['BZ'], 'stracone': s['BS'],
            'bilans': s['BZ'] - s['BS'], 'wygrane': s['W'], 'remisy': s['R'], 'porażki': s['P'], 'forma': forma,
            'dom_w': s['Dom_W'], 'dom_r': s['Dom_R'], 'dom_p': s['Dom_P'],
            'wyj_w': s['Wyj_W'], 'wyj_r': s['Wyj_R'], 'wyj_p': s['Wyj_P']
        })
        
    df = pd.DataFrame(table_data)
    if not df.empty:
        df = df.sort_values(by=['punkty', 'bilans', 'strzelone'], ascending=[False, False, False])
        df.reset_index(drop=True, inplace=True)
        df.index += 1
        df['Miejsce'] = df.index
    return df

# --- 4. INTERFEJS ---

data_sheets = load_all_data(EXCEL_FILE)

if data_sheets:
    st.sidebar.title("Menu")
    sheet_names = list(data_sheets.keys())
    special = ['Tabela', 'Strzelcy', 'Legenda', 'Info']
    team_names = sorted([n for n in sheet_names if n not in special])
    matches_dict = aggregate_matches(data_sheets, team_names)
    
    page = st.sidebar.radio("Wybierz widok", ["🏆 Tabela Ligowa", "📅 Terminarz", "🎯 Strzelcy", "⚽ Drużyny"])
    
    if page == "🏆 Tabela Ligowa":
        st.title("Tabela Ligi Mistrzów 25/26 (Live)")
        df = calculate_table_from_matches(matches_dict)
        if not df.empty:
            df['logo_url'] = df['klub'].apply(get_club_logo_url)
            st.dataframe(df, use_container_width=True, hide_index=True,
                column_config={
                    "logo_url": st.column_config.ImageColumn("Herb", width="small"),
                    "bilans": st.column_config.ProgressColumn("Bilans", min_value=-20, max_value=50, format="%d"),
                    "Miejsce": st.column_config.NumberColumn("#", format="%d")
                },
                column_order=['Miejsce', 'logo_url', 'klub', 'mecze', 'punkty', 'strzelone', 'stracone', 'bilans', 'wygrane', 'remisy', 'porażki', 'forma']
            )
        else: st.info("Brak danych.")

    elif page == "📅 Terminarz":
        st.title("Terminarz (Wyniki z goli)")
        df_sched = pd.DataFrame(list(matches_dict.values()))
        if not df_sched.empty:
            df_sched = df_sched.sort_values('Kolejka')
            rounds = sorted(df_sched['Kolejka'].unique())
            if rounds:
                sel_round = st.selectbox("Wybierz kolejkę", rounds)
                for _, row in df_sched[df_sched['Kolejka'] == sel_round].iterrows():
                    h, g, res = row['Gospodarze'], row['Goście'], row['Wynik']
                    sh = ", ".join(row['Strzelcy_H'])
                    sa = ", ".join(row['Strzelcy_A'])
                    
                    with st.container():
                        c1, c2, c3, c4, c5 = st.columns([0.5, 3, 1, 3, 0.5])
                        with c1: 
                            if get_club_logo_url(h): st.image(get_club_logo_url(h), width=50)
                        with c2:
                            st.markdown(f"<div style='text-align:right; font-weight:bold'>{h}</div>", unsafe_allow_html=True)
                            if sh: st.markdown(f"<div style='text-align:right; font-size:0.8em; color:gray'>⚽ {sh}</div>", unsafe_allow_html=True)
                        with c3:
                            bg = "#a3ffa3" if res != "-" else "#e0e0e0"
                            st.markdown(f"<div style='background:{bg}; border-radius:5px; text-align:center; font-weight:bold; padding:5px'>{res}</div>", unsafe_allow_html=True)
                        with c4:
                            st.markdown(f"<div style='text-align:left; font-weight:bold'>{g}</div>", unsafe_allow_html=True)
                            if sa: st.markdown(f"<div style='text-align:left; font-size:0.8em; color:gray'>⚽ {sa}</div>", unsafe_allow_html=True)
                        with c5:
                            if get_club_logo_url(g): st.image(get_club_logo_url(g), width=50)
                        st.divider()
            else: st.info("Brak kolejek.")
        else: st.info("Brak terminarza.")

    elif page == "🎯 Strzelcy":
        st.title("Najlepsi Strzelcy")
        if 'Strzelcy' in data_sheets:
            df_s = data_sheets['Strzelcy']
            df_s.columns = [str(c).lower().strip() for c in df_s.columns]
            if 'kraj' in df_s.columns: df_s['flaga_url'] = df_s['kraj'].apply(get_flag_url)
            cols = ['flaga_url'] + [c for c in df_s.columns if c not in ['flaga_url', 'kraj']]
            st.dataframe(df_s[[c for c in cols if c in df_s.columns]], use_container_width=True, hide_index=True,
                column_config={"flaga_url": st.column_config.ImageColumn("Kraj", width="small"), "gole": st.column_config.ProgressColumn("Gole", format="%d", min_value=0, max_value=30)})
        else: st.warning("Brak arkusza.")

    elif page == "⚽ Drużyny":
        st.title("Profil Drużyny")
        sel = st.sidebar.selectbox("Wybierz", team_names)
        if sel:
            df_p, df_s, df_m = process_team_sheet(data_sheets[sel], sel)
            stats = calculate_table_from_matches(matches_dict)
            t_stat = stats[stats['klub'] == sel].iloc[0] if not stats[stats['klub'] == sel].empty else None
            
            c1, c2 = st.columns([1, 5])
            with c1:
                if get_club_logo_url(sel): st.image(get_club_logo_url(sel), width=100)
            with c2:
                st.header(sel)
                if t_stat is not None: st.caption(f"Miejsce: {t_stat['Miejsce']} | Pkt: {t_stat['punkty']} | Bramki: {t_stat['strzelone']}:{t_stat['stracone']}")

            # NOWA KOLEJNOŚĆ ZAKŁADEK
            tab1, tab2, tab3 = st.tabs(["👥 Kadra", "📊 Statystyki", "📅 Mecze"])
            
            with tab1: # KADRA
                if not df_p.empty:
                    cols = ['numer', 'flaga_url', 'imię i nazwisko', 'pozycja', 'wiek', 'mecze', 'minuty', 'gole', 'asysty']
                    st.dataframe(df_p[[c for c in cols if c in df_p.columns]], use_container_width=True, hide_index=True, column_config={"flaga_url": st.column_config.ImageColumn("", width="small")})

            with tab2: # STATYSTYKI
                if t_stat is not None:
                    st.metric("Bilans", f"{t_stat['wygrane']}W - {t_stat['remisy']}R - {t_stat['porażki']}P")
                if not df_p.empty and 'gole' in df_p.columns:
                    sc = df_p[df_p['gole']>0].sort_values('gole')
                    if not sc.empty: st.plotly_chart(px.bar(sc, x='gole', y='imię i nazwisko', orientation='h', title="Strzelcy"), use_container_width=True)

            with tab3: # MECZE
                if not df_m.empty: st.dataframe(df_m, use_container_width=True, hide_index=True)
else:
    st.error(f"Brak pliku {EXCEL_FILE}")
