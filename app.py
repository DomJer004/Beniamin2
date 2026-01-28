import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Liga Mistrzów 25/26", layout="wide", page_icon="⚽")

EXCEL_FILE = "Liga Mistrzów 25_26.xlsx"

# --- 1. CONFIG & SŁOWNIKI ---

# Funkcja pomocnicza do normalizacji nazw (usuwa spacje, zmniejsza litery)
def normalize_key(name):
    if not isinstance(name, str): return ""
    return name.strip().lower()

# Rozszerzona baza herbów - klucze znormalizowane (lowercase)
CLUB_LOGOS_RAW = {
    # Anglia
    "arsenal": "https://upload.wikimedia.org/wikipedia/en/5/53/Arsenal_FC.svg",
    "aston villa": "https://upload.wikimedia.org/wikipedia/en/9/9f/Aston_Villa_logo.svg",
    "liverpool": "https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg",
    "manchester city": "https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
    "city": "https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
    "chelsea": "https://upload.wikimedia.org/wikipedia/en/c/cc/Chelsea_FC.svg",
    "tottenham hotspur": "https://upload.wikimedia.org/wikipedia/en/b/b4/Tottenham_Hotspur.svg",
    "tottenham": "https://upload.wikimedia.org/wikipedia/en/b/b4/Tottenham_Hotspur.svg",
    "newcastle united": "https://upload.wikimedia.org/wikipedia/en/5/56/Newcastle_United_Logo.svg",
    "newcastle": "https://upload.wikimedia.org/wikipedia/en/5/56/Newcastle_United_Logo.svg",
    
    # Hiszpania
    "real madryt": "https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg",
    "real": "https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg",
    "barcelona": "https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg",
    "barca": "https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg",
    "atlético madryt": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "atletico madryt": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "atlético": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "atletico": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "girona": "https://upload.wikimedia.org/wikipedia/en/9/90/Girona_FC_Crest.svg",
    "athletic bilbao": "https://upload.wikimedia.org/wikipedia/en/9/98/Club_Athletic_Bilbao_logo.svg",
    "bilbao": "https://upload.wikimedia.org/wikipedia/en/9/98/Club_Athletic_Bilbao_logo.svg",
    "villarreal": "https://upload.wikimedia.org/wikipedia/en/7/70/Villarreal_CF_logo.svg",
    
    # Niemcy
    "bayern monachium": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_München_logo_%282017%29.svg",
    "bayern": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_München_logo_%282017%29.svg",
    "borussia dortmund": "https://upload.wikimedia.org/wikipedia/commons/6/67/Borussia_Dortmund_logo.svg",
    "borussia": "https://upload.wikimedia.org/wikipedia/commons/6/67/Borussia_Dortmund_logo.svg",
    "bayer leverkusen": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
    "leverkusen": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
    "rb leipzig": "https://upload.wikimedia.org/wikipedia/en/0/04/RB_Leipzig_2014_logo.svg",
    "leipzig": "https://upload.wikimedia.org/wikipedia/en/0/04/RB_Leipzig_2014_logo.svg",
    "stuttgart": "https://upload.wikimedia.org/wikipedia/commons/e/eb/VfB_Stuttgart_1893_Logo.svg",
    "vfb stuttgart": "https://upload.wikimedia.org/wikipedia/commons/e/eb/VfB_Stuttgart_1893_Logo.svg",
    "eintracht frankfurt": "https://upload.wikimedia.org/wikipedia/commons/0/04/Eintracht_Frankfurt_Logo.svg",
    "frankfurt": "https://upload.wikimedia.org/wikipedia/commons/0/04/Eintracht_Frankfurt_Logo.svg",
    
    # Włochy
    "inter mediolan": "https://upload.wikimedia.org/wikipedia/commons/0/05/FC_Internazionale_Milano_2021.svg",
    "inter": "https://upload.wikimedia.org/wikipedia/commons/0/05/FC_Internazionale_Milano_2021.svg",
    "ac milan": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Logo_of_AC_Milan.svg",
    "milan": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Logo_of_AC_Milan.svg",
    "juventus": "https://upload.wikimedia.org/wikipedia/commons/5/51/Juventus_FC_2017_icon_%28black%29.svg",
    "atalanta": "https://upload.wikimedia.org/wikipedia/en/6/66/AtalantaBC.svg",
    "bologna": "https://upload.wikimedia.org/wikipedia/en/5/5b/Bologna_F.C._1909_logo.svg",
    "napoli": "https://upload.wikimedia.org/wikipedia/commons/2/2d/SSC_Neapel.svg",
    
    # Francja
    "paris saint-germain": "https://upload.wikimedia.org/wikipedia/en/a/a7/Paris_Saint-Germain_F.C..svg",
    "psg": "https://upload.wikimedia.org/wikipedia/en/a/a7/Paris_Saint-Germain_F.C..svg",
    "monaco": "https://upload.wikimedia.org/wikipedia/en/b/ba/AS_Monaco_FC.svg",
    "brest": "https://upload.wikimedia.org/wikipedia/en/0/05/Stade_Brestois_29_logo.svg",
    "lille": "https://upload.wikimedia.org/wikipedia/en/6/6f/Lille_OSC_2018_logo.svg",
    "olympique marsylia": "https://upload.wikimedia.org/wikipedia/commons/d/d8/Olympique_Marseille_logo.svg",
    "marsylia": "https://upload.wikimedia.org/wikipedia/commons/d/d8/Olympique_Marseille_logo.svg",
    
    # Inne
    "sporting cp": "https://upload.wikimedia.org/wikipedia/en/e/e1/Sporting_Clube_de_Portugal_%28Complex%29.svg",
    "sporting": "https://upload.wikimedia.org/wikipedia/en/e/e1/Sporting_Clube_de_Portugal_%28Complex%29.svg",
    "benfica": "https://upload.wikimedia.org/wikipedia/en/a/a2/SL_Benfica_logo.svg",
    "fc porto": "https://upload.wikimedia.org/wikipedia/en/f/f1/FC_Porto.svg",
    "psv eindhoven": "https://upload.wikimedia.org/wikipedia/en/0/05/PSV_Eindhoven.svg",
    "psv": "https://upload.wikimedia.org/wikipedia/en/0/05/PSV_Eindhoven.svg",
    "feyenoord": "https://upload.wikimedia.org/wikipedia/en/e/e3/Feyenoord_logo.svg",
    "club brugge": "https://upload.wikimedia.org/wikipedia/en/d/d0/Club_Brugge_KV_logo.svg",
    "brugge": "https://upload.wikimedia.org/wikipedia/en/d/d0/Club_Brugge_KV_logo.svg",
    "celtic": "https://upload.wikimedia.org/wikipedia/en/3/35/Celtic_FC.svg",
    "sturm graz": "https://upload.wikimedia.org/wikipedia/commons/c/cc/SK_Sturm_Graz_Logo.svg",
    "rb salzburg": "https://upload.wikimedia.org/wikipedia/en/7/77/FC_Red_Bull_Salzburg_logo.svg",
    "szachtar donieck": "https://upload.wikimedia.org/wikipedia/en/a/a1/FC_Shakhtar_Donetsk.svg",
    "szachtar": "https://upload.wikimedia.org/wikipedia/en/a/a1/FC_Shakhtar_Donetsk.svg",
    "dinamo zagrzeb": "https://upload.wikimedia.org/wikipedia/en/f/f6/NK_Dinamo_Zagreb.svg",
    "crvena zvezda": "https://upload.wikimedia.org/wikipedia/commons/2/2a/Red_Star_Belgrade_logo.svg",
    "young boys": "https://upload.wikimedia.org/wikipedia/en/6/6b/BSC_Young_Boys_logo.svg",
    "sparta praga": "https://upload.wikimedia.org/wikipedia/en/3/39/AC_Sparta_Praha_logo.svg",
    "slovan bratysława": "https://upload.wikimedia.org/wikipedia/en/8/8b/Slovan_Bratislava_logo.svg",
    "galatasaray": "https://upload.wikimedia.org/wikipedia/en/3/31/Galatasaray_Star_Logo.svg",
    "fc kopenhaga": "https://upload.wikimedia.org/wikipedia/en/9/93/FC_København.svg",
    "kopenhaga": "https://upload.wikimedia.org/wikipedia/en/9/93/FC_København.svg",
    "bodo/glimt": "https://upload.wikimedia.org/wikipedia/en/2/22/FK_Bodø_Glimt.svg",
    "bodo": "https://upload.wikimedia.org/wikipedia/en/2/22/FK_Bodø_Glimt.svg"
}

COUNTRY_CODES = {
    "anglia": "gb-eng", "szkocja": "gb-sct", "walia": "gb-wls", "polska": "pl", "hiszpania": "es", 
    "niemcy": "de", "włochy": "it", "francja": "fr", "portugalia": "pt", "holandia": "nl", 
    "belgia": "be", "chorwacja": "hr", "dania": "dk", "szwecja": "se", "norwegia": "no", 
    "irlandia": "ie", "czechy": "cz", "słowacja": "sk", "ukraina": "ua", "turcja": "tr", 
    "grecja": "gr", "szwajcaria": "ch", "austria": "at", "węgry": "hu", "rumunia": "ro", 
    "bułgaria": "bg", "serbia": "rs", "bośnia": "ba", "brazylia": "br", "argentyna": "ar", 
    "urugwaj": "uy", "kolumbia": "co", "usa": "us", "meksyk": "mx", "japonia": "jp", 
    "korea": "kr", "kanada": "ca", "maroko": "ma", "senegal": "sn", "egipt": "eg"
}

def get_flag_url(nationality_str):
    if not isinstance(nationality_str, str) or not nationality_str.strip(): return None
    clean_nat = normalize_key(nationality_str).split(",")[0].split("/")[0]
    # Mapowania specyficzne
    if "konaga" in clean_nat or "konga" in clean_nat: return "https://flagcdn.com/w40/cd.png"
    code = COUNTRY_CODES.get(clean_nat)
    if not code:
        # Fallback - spróbuj znaleźć część wspólną
        for k, v in COUNTRY_CODES.items():
            if k in clean_nat:
                code = v
                break
    return f"https://flagcdn.com/w40/{code}.png" if code else None

def get_club_logo_url(club_name):
    if not isinstance(club_name, str): return None
    key = normalize_key(club_name)
    return CLUB_LOGOS_RAW.get(key, None)

def repair_excel_date_score(value):
    if pd.isna(value): return None
    val_str = str(value).strip()
    # Jeżeli format to np. "10-maj", Excel mógł to zmienić na datę.
    # W kontekście wyników piłkarskich szukamy "-".
    if "-" in val_str and len(val_str) < 8: return val_str
    try:
        dt = pd.to_datetime(value, errors='coerce')
        if not pd.isna(dt):
            return f"{dt.day}-{dt.month}"
    except:
        pass
    return val_str

# --- 2. ŁADOWANIE DANYCH ---

@st.cache_data
def load_all_data(file_path):
    if not os.path.exists(file_path): return None
    try: return pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
    except: return None

def clean_matches_table(df, start_row_idx):
    """Czyści tabelę meczową, dbając o unikalne nazwy kolumn."""
    header_row = df.iloc[start_row_idx]
    new_columns, indices = [], []
    seen = {}
    
    for i, c in enumerate(header_row):
        if pd.isna(c) or str(c).strip() == "" or str(c).lower() == "nan": 
            # Czasem kolumny bez nazwy to kolumny ze strzelcami
            col_name = f"Info_{i}"
        else:
            col_name = str(c).strip()
            
        seen[col_name] = seen.get(col_name, 0) + 1
        final_name = f"{col_name}_{seen[col_name]}" if seen[col_name] > 1 else col_name
        new_columns.append(final_name)
        indices.append(i)
    
    matches = df.iloc[start_row_idx+1:, indices].copy()
    matches.columns = new_columns
    
    # Normalizacja nazw kolumn do lowercase dla łatwiejszego szukania
    matches.columns = [str(c).lower().strip() for c in matches.columns]
    
    if 'wynik' in matches.columns:
        matches['wynik'] = matches['wynik'].apply(repair_excel_date_score)
        
    return matches

def process_team_sheet(df, team_name):
    try:
        # Znajdź początek tabeli meczowej (szukamy słowa 'kolejka')
        # Używamy pętli dla pewności
        match_idx = -1
        for idx, row in df.iterrows():
            if row.astype(str).str.contains('kolejka', case=False).any():
                match_idx = idx
                break
        
        if match_idx == -1: match_idx = len(df)
        
        df_top = df.iloc[:match_idx].copy()
        
        # Szukanie sztabu
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

        # Czyszczenie piłkarzy
        if not df_players.empty:
            # Ustaw nagłówek z pierwszego wiersza, jeśli kolumny to int
            if isinstance(df_players.columns[0], int):
                df_players.columns = df_players.iloc[0].astype(str).str.lower().str.strip()
                df_players = df_players[1:]
                
            # Normalizacja nazw kolumn
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

        # Mecze
        df_matches = pd.DataFrame()
        if match_idx < len(df):
            df_matches = clean_matches_table(df, match_idx)

        return df_players, df_staff, df_matches

    except Exception as e:
        # st.error(f"Błąd przetwarzania {team_name}: {e}") # Debug
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- 3. LOGIKA BIZNESOWA ---

def calculate_live_table(data_sheets):
    stats = {}
    ignore = ['Tabela', 'Strzelcy', 'Legenda', 'Info']
    processed_matches = set()
    
    for sheet_name, df in data_sheets.items():
        if sheet_name in ignore: continue
        
        _, _, df_m = process_team_sheet(df, sheet_name)
        
        if not df_m.empty and 'wynik' in df_m.columns and 'gospodarze' in df_m.columns:
            for _, row in df_m.iterrows():
                host = str(row['gospodarze']).strip()
                guest = str(row['goście']).strip()
                wynik = str(row['wynik']).strip()
                kolejka = str(row.get('kolejka', '0')).strip()
                
                if host.lower() == 'nan' or guest.lower() == 'nan': continue
                
                match_id = "-".join(sorted([host, guest])) + f"-k{kolejka}"
                if match_id in processed_matches: continue
                
                # Inicjalizacja
                for t in [host, guest]:
                    if t not in stats: stats[t] = {'M':0, 'Pkt':0, 'BZ':0, 'BS':0, 'W':0, 'R':0, 'P':0}

                # Parsowanie
                if '-' in wynik:
                    parts = wynik.split('-')
                    if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
                        processed_matches.add(match_id)
                        h_goals = int(parts[0])
                        a_goals = int(parts[1])
                        
                        stats[host]['M'] += 1
                        stats[host]['BZ'] += h_goals
                        stats[host]['BS'] += a_goals
                        
                        stats[guest]['M'] += 1
                        stats[guest]['BZ'] += a_goals
                        stats[guest]['BS'] += h_goals
                        
                        if h_goals > a_goals:
                            stats[host]['Pkt'] += 3
                            stats[host]['W'] += 1
                            stats[guest]['P'] += 1
                        elif a_goals > h_goals:
                            stats[guest]['Pkt'] += 3
                            stats[guest]['W'] += 1
                            stats[host]['P'] += 1
                        else:
                            stats[host]['Pkt'] += 1
                            stats[host]['R'] += 1
                            stats[guest]['Pkt'] += 1
                            stats[guest]['R'] += 1

    table_data = []
    for team, s in stats.items():
        table_data.append({
            'klub': team,
            'mecze': s['M'],
            'punkty': s['Pkt'],
            'strzelone': s['BZ'],
            'stracone': s['BS'],
            'bilans': s['BZ'] - s['BS'],
            'wygrane': s['W'],
            'remisy': s['R'],
            'porażki': s['P']
        })
        
    df_live = pd.DataFrame(table_data)
    if not df_live.empty:
        df_live = df_live.sort_values(by=['punkty', 'bilans', 'strzelone'], ascending=[False, False, False])
        df_live.reset_index(drop=True, inplace=True)
        df_live.index += 1
        df_live['Miejsce'] = df_live.index
        
    return df_live

# --- 4. INTERFEJS ---

data_sheets = load_all_data(EXCEL_FILE)

if data_sheets:
    st.sidebar.title("Menu")
    sheet_names = list(data_sheets.keys())
    special_sheets = ['Tabela', 'Strzelcy', 'Legenda', 'Info']
    team_names = sorted([n for n in sheet_names if n not in special_sheets])
    
    page = st.sidebar.radio("Wybierz widok", ["🏆 Tabela Ligowa", "📅 Terminarz", "🎯 Strzelcy", "⚽ Drużyny"])
    
    if page == "🏆 Tabela Ligowa":
        st.title("Tabela Ligi Mistrzów 25/26 (Live)")
        df_live_table = calculate_live_table(data_sheets)
        
        if not df_live_table.empty:
            df_live_table['logo_url'] = df_live_table['klub'].apply(get_club_logo_url)
            
            st.dataframe(
                df_live_table,
                use_container_width=True, hide_index=True,
                column_config={
                    "logo_url": st.column_config.ImageColumn("Herb", width="small"),
                    "bilans": st.column_config.ProgressColumn("Bilans", min_value=-20, max_value=50, format="%d"),
                    "Miejsce": st.column_config.NumberColumn("#", format="%d")
                },
                column_order=['Miejsce', 'logo_url', 'klub', 'mecze', 'punkty', 'strzelone', 'stracone', 'bilans', 'wygrane', 'remisy', 'porażki']
            )
        else:
            st.info("Brak rozegranych meczów lub błąd odczytu danych.")

    elif page == "📅 Terminarz":
        st.title("Terminarz i Wyniki")
        all_matches = []
        processed_ids = set()
        
        for name in team_names:
            _, _, df_m = process_team_sheet(data_sheets[name], name)
            if not df_m.empty and 'wynik' in df_m.columns:
                # Szukamy kolumn strzelców szerzej (gole, strzelcy, bramki, info)
                potential_cols = [c for c in df_m.columns if any(x in str(c).lower() for x in ['gole', 'strzelcy', 'bramki', 'info'])]
                
                for _, row in df_m.iterrows():
                    h, g = str(row.get('gospodarze', '')).strip(), str(row.get('goście', '')).strip()
                    k = row.get('kolejka', '0')
                    
                    if not h or h.lower()=='nan' or not g: continue
                    
                    mid = "-".join(sorted([h, g])) + f"-k{k}"
                    if mid in processed_ids: continue
                    processed_ids.add(mid)
                    
                    # Zbieranie strzelców
                    scorers_list = []
                    for sc in potential_cols:
                        val = str(row[sc]).strip()
                        # Filtruj śmieciowe dane
                        if val and val.lower() != 'nan' and val != '0' and len(val) > 2:
                            scorers_list.append(val)
                    
                    scorers_txt = ", ".join(scorers_list)
                    
                    res = row['wynik']
                    res_display = str(res) if pd.notna(res) and str(res).strip() not in ["", "nan"] else "-"

                    all_matches.append({
                        "Kolejka": int(k) if str(k).isdigit() else 0,
                        "Gospodarze": h, "Goście": g, "Wynik": res_display,
                        "Strzelcy": scorers_txt,
                        "Logo_H": get_club_logo_url(h), "Logo_A": get_club_logo_url(g)
                    })
        
        df_sched = pd.DataFrame(all_matches).sort_values('Kolejka')
        
        if not df_sched.empty:
            rounds = sorted(df_sched['Kolejka'].unique())
            sel_round = st.selectbox("Wybierz kolejkę", rounds)
            
            for _, row in df_sched[df_sched['Kolejka'] == sel_round].iterrows():
                with st.container():
                    # Lepszy layout dla meczu
                    c1, c2, c3, c4, c5 = st.columns([0.5, 2, 1, 2, 0.5])
                    with c1: 
                        if row['Logo_H']: st.image(row['Logo_H'], width=50)
                    with c2: 
                        st.markdown(f"<div style='text-align:right; font-weight:bold; padding-top:10px'>{row['Gospodarze']}</div>", unsafe_allow_html=True)
                    with c3: 
                        bg_color = "#e0e0e0" if row['Wynik'] == "-" else "#a3ffa3"
                        st.markdown(f"<div style='background-color:{bg_color}; border-radius:5px; text-align:center; padding:5px; font-weight:bold; color:black'>{row['Wynik']}</div>", unsafe_allow_html=True)
                    with c4: 
                        st.markdown(f"<div style='text-align:left; font-weight:bold; padding-top:10px'>{row['Goście']}</div>", unsafe_allow_html=True)
                    with c5: 
                        if row['Logo_A']: st.image(row['Logo_A'], width=50)
                    
                    if row['Strzelcy']:
                        st.markdown(f"<div style='text-align:center; font-size:0.8em; color:gray'>⚽ {row['Strzelcy']}</div>", unsafe_allow_html=True)
                    st.divider()
        else:
            st.info("Brak danych w terminarzu.")

    elif page == "🎯 Strzelcy":
        st.title("Najlepsi Strzelcy")
        if 'Strzelcy' in data_sheets:
            df_s = data_sheets['Strzelcy']
            # Normalizacja kolumn dla bezpieczeństwa
            df_s.columns = [str(c).lower().strip() for c in df_s.columns]
            
            if 'kraj' in df_s.columns: df_s['flaga_url'] = df_s['kraj'].apply(get_flag_url)
            
            # Konfiguracja wyświetlania
            cols_to_show = []
            if 'flaga_url' in df_s.columns: cols_to_show.append('flaga_url')
            
            # Dodaj pozostałe kolumny (pomijając te techniczne)
            exclude = ['flaga_url', 'kraj']
            cols_to_show.extend([c for c in df_s.columns if c not in exclude])
            
            st.dataframe(
                df_s[cols_to_show], 
                use_container_width=True, hide_index=True,
                column_config={
                    "flaga_url": st.column_config.ImageColumn("Kraj", width="small"),
                    "gole": st.column_config.ProgressColumn("Gole", format="%d", min_value=0, max_value=20)
                }
            )
        else:
            st.warning("Brak zakładki 'Strzelcy' w pliku Excel.")

    elif page == "⚽ Drużyny":
        st.title("Statystyki Drużyn")
        selected_team = st.sidebar.selectbox("Wybierz drużynę", team_names)
        
        if selected_team:
            df_p, df_s, df_m = process_team_sheet(data_sheets[selected_team], selected_team)
            
            # HEADER
            col_l, col_t = st.columns([1, 5])
            with col_l:
                logo = get_club_logo_url(selected_team)
                if logo: st.image(logo, width=100)
            with col_t:
                st.header(selected_team)
                # Szybkie KPI
                if not df_p.empty and 'gole' in df_p.columns:
                    total_goals = df_p['gole'].sum()
                    top_scorer = df_p.loc[df_p['gole'].idxmax()]['imię i nazwisko'] if total_goals > 0 else "-"
                    st.caption(f"Gole łącznie: **{total_goals}** | Najlepszy strzelec: **{top_scorer}**")

            tab1, tab2, tab3 = st.tabs(["📊 Statystyki i Wykresy", "👥 Kadra", "📅 Mecze"])
            
            with tab1:
                if not df_p.empty:
                    c1, c2 = st.columns(2)
                    with c1:
                        if 'gole' in df_p.columns:
                            # Filtrujemy tylko tych co strzelili
                            scorers = df_p[df_p['gole'] > 0].sort_values('gole', ascending=True)
                            if not scorers.empty:
                                fig_g = px.bar(scorers, x='gole', y='imię i nazwisko', orientation='h', 
                                             title="Najlepsi Strzelcy", text='gole',
                                             color='gole', color_continuous_scale='Reds')
                                fig_g.update_layout(showlegend=False, xaxis_title="", yaxis_title="")
                                st.plotly_chart(fig_g, use_container_width=True)
                            else:
                                st.info("Brak goli w zespole.")
                    
                    with c2:
                        if 'minuty' in df_p.columns:
                            # Top 10 minut
                            minutes = df_p.nlargest(10, 'minuty').sort_values('minuty', ascending=True)
                            fig_m = px.bar(minutes, x='minuty', y='imię i nazwisko', orientation='h',
                                         title="Najwięcej Minut", text='minuty',
                                         color='minuty', color_continuous_scale='Blues')
                            fig_m.update_layout(showlegend=False, xaxis_title="", yaxis_title="")
                            st.plotly_chart(fig_m, use_container_width=True)

                    # Nowy wykres: Scatter plot (Efektywność)
                    if 'minuty' in df_p.columns and 'gole' in df_p.columns:
                        st.subheader("Efektywność (Gole vs Minuty)")
                        scatter_df = df_p[df_p['gole'] > 0]
                        if not scatter_df.empty:
                            fig_s = px.scatter(scatter_df, x='minuty', y='gole', size='gole', hover_name='imię i nazwisko',
                                             color='pozycja' if 'pozycja' in df_p.columns else None,
                                             title="Kto strzela najczęściej względem czasu gry?")
                            st.plotly_chart(fig_s, use_container_width=True)

            with tab2:
                if not df_p.empty:
                    cols_p = ['numer', 'flaga_url', 'imię i nazwisko', 'pozycja', 'wiek', 'mecze', 'minuty', 'gole', 'asysty']
                    final_p = [c for c in cols_p if c in df_p.columns]
                    st.dataframe(
                        df_p[final_p], use_container_width=True, hide_index=True,
                        column_config={
                            "flaga_url": st.column_config.ImageColumn("", width="small"),
                            "numer": st.column_config.NumberColumn("#", format="%d"),
                            "gole": st.column_config.NumberColumn("⚽"),
                            "asysty": st.column_config.NumberColumn("🅰️")
                        }
                    )
            
            with tab3:
                if not df_m.empty and 'wynik' in df_m.columns:
                    st.dataframe(df_m, use_container_width=True, hide_index=True)
                else:
                    st.info("Brak rozegranych meczów.")
else:
    st.error(f"Nie znaleziono pliku {EXCEL_FILE}. Upewnij się, że jest w tym samym folderze co app.py.")
