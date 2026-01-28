import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Liga Mistrzów 25/26", layout="wide", page_icon="⚽")

EXCEL_FILE = "Liga Mistrzów 25_26.xlsx"

# --- 1. CONFIG & SŁOWNIKI ---

def normalize_key(name):
    if not isinstance(name, str): return ""
    return name.strip().lower()

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
    if "konaga" in clean_nat or "konga" in clean_nat: return "https://flagcdn.com/w40/cd.png"
    code = COUNTRY_CODES.get(clean_nat)
    if not code:
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
    header_row = df.iloc[start_row_idx]
    new_columns, indices = [], []
    seen = {}
    
    for i, c in enumerate(header_row):
        col_name = str(c).strip() if pd.notna(c) and str(c).strip() != "" and str(c).lower() != "nan" else f"Info_{i}"
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

    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- 3. AGREGACJA DANYCH MECZOWYCH (DLA TABELI I TERMINARZA) ---

def aggregate_matches(data_sheets, team_names):
    """
    Tworzy słownik unikalnych meczów, zbierając strzelców z arkuszy obu drużyn.
    Klucz: ID meczu (Host-Guest-Kolejka).
    """
    matches_dict = {}
    
    for team in team_names:
        _, _, df_m = process_team_sheet(data_sheets[team], team)
        
        if not df_m.empty and 'wynik' in df_m.columns:
            # Szukamy kolumn strzelców (lokalnie w tym arkuszu, więc to strzelcy TEJ drużyny)
            potential_cols = [c for c in df_m.columns if any(x in str(c).lower() for x in ['gole', 'strzelcy', 'bramki', 'info'])]
            
            for _, row in df_m.iterrows():
                h = str(row.get('gospodarze', '')).strip()
                g = str(row.get('goście', '')).strip()
                k = str(row.get('kolejka', '0')).strip()
                res = str(row.get('wynik', '')).strip()

                if not h or h.lower()=='nan' or not g: continue
                
                # Unikalne ID meczu (zawsze alfabetycznie, żeby sparować arkusz A i B)
                match_id = "-".join(sorted([h, g])) + f"-k{k}"
                
                if match_id not in matches_dict:
                    matches_dict[match_id] = {
                        "Kolejka": int(k) if k.isdigit() else 0,
                        "Gospodarze": h, 
                        "Goście": g, 
                        "Wynik": res if res and res.lower() != 'nan' else "-",
                        "Strzelcy_H": [],
                        "Strzelcy_A": []
                    }
                
                # Aktualizacja wyniku (jeśli w jednym arkuszu jest pusty, a w drugim wpisany)
                if matches_dict[match_id]["Wynik"] == "-" and res and res.lower() != 'nan':
                    matches_dict[match_id]["Wynik"] = res

                # Zbieranie strzelców z TEGO arkusza
                # Musimy ustalić, czy 'team' (właściciel arkusza) jest Gospodarzem czy Gościem w tym meczu
                is_home = (normalize_key(team) == normalize_key(h) or normalize_key(team) in normalize_key(h))
                is_away = (normalize_key(team) == normalize_key(g) or normalize_key(team) in normalize_key(g))
                
                # Pobranie tekstu strzelców z wiersza
                scorers_list = []
                for sc in potential_cols:
                    val = str(row[sc]).strip()
                    if val and val.lower() != 'nan' and val != '0' and len(val) > 2:
                        scorers_list.append(val)
                
                # Dodajemy do odpowiedniej listy w słowniku meczu
                if scorers_list:
                    if is_home:
                        matches_dict[match_id]["Strzelcy_H"].extend(scorers_list)
                    elif is_away:
                        matches_dict[match_id]["Strzelcy_A"].extend(scorers_list)
                    # Jeśli nazwa w arkuszu różni się drastycznie od nazwy drużyny (rzadkie), 
                    # można dodać logikę fuzzy match, ale zazwyczaj nazwa arkusza = nazwa klubu.

    return matches_dict

def calculate_table_from_matches(matches_dict):
    stats = {}
    
    for mid, data in matches_dict.items():
        h, g = data['Gospodarze'], data['Goście']
        res = data['Wynik']
        
        # Inicjalizacja
        for t in [h, g]:
            if t not in stats: stats[t] = {'M':0, 'Pkt':0, 'BZ':0, 'BS':0, 'W':0, 'R':0, 'P':0, 
                                           'Dom_M':0, 'Dom_W':0, 'Dom_R':0, 'Dom_P':0,
                                           'Wyj_M':0, 'Wyj_W':0, 'Wyj_R':0, 'Wyj_P':0,
                                           'Forma': []}

        if '-' in res:
            parts = res.split('-')
            if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
                hg = int(parts[0])
                ag = int(parts[1])
                
                # Gospodarz
                stats[h]['M'] += 1
                stats[h]['BZ'] += hg
                stats[h]['BS'] += ag
                stats[h]['Dom_M'] += 1
                
                # Gość
                stats[g]['M'] += 1
                stats[g]['BZ'] += ag
                stats[g]['BS'] += hg
                stats[g]['Wyj_M'] += 1
                
                if hg > ag:
                    stats[h]['Pkt'] += 3
                    stats[h]['W'] += 1; stats[h]['Dom_W'] += 1
                    stats[h]['Forma'].append('W')
                    stats[g]['P'] += 1; stats[g]['Wyj_P'] += 1
                    stats[g]['Forma'].append('P')
                elif ag > hg:
                    stats[g]['Pkt'] += 3
                    stats[g]['W'] += 1; stats[g]['Wyj_W'] += 1
                    stats[g]['Forma'].append('W')
                    stats[h]['P'] += 1; stats[h]['Dom_P'] += 1
                    stats[h]['Forma'].append('P')
                else:
                    stats[h]['Pkt'] += 1
                    stats[h]['R'] += 1; stats[h]['Dom_R'] += 1
                    stats[h]['Forma'].append('R')
                    stats[g]['Pkt'] += 1
                    stats[g]['R'] += 1; stats[g]['Wyj_R'] += 1
                    stats[g]['Forma'].append('R')

    table_data = []
    for team, s in stats.items():
        # Ostatnie 5 meczów
        forma_str = "".join(s['Forma'][-5:]).replace("W", "✅").replace("R", "➖").replace("P", "❌")
        
        table_data.append({
            'klub': team,
            'mecze': s['M'],
            'punkty': s['Pkt'],
            'strzelone': s['BZ'],
            'stracone': s['BS'],
            'bilans': s['BZ'] - s['BS'],
            'wygrane': s['W'],
            'remisy': s['R'],
            'porażki': s['P'],
            'forma': forma_str,
            # Staty ukryte do szczegółów
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
    special_sheets = ['Tabela', 'Strzelcy', 'Legenda', 'Info']
    team_names = sorted([n for n in sheet_names if n not in special_sheets])
    
    # Przetwarzamy mecze raz na początku
    matches_dict = aggregate_matches(data_sheets, team_names)
    
    page = st.sidebar.radio("Wybierz widok", ["🏆 Tabela Ligowa", "📅 Terminarz", "🎯 Strzelcy", "⚽ Drużyny"])
    
    if page == "🏆 Tabela Ligowa":
        st.title("Tabela Ligi Mistrzów 25/26 (Live)")
        df_live_table = calculate_table_from_matches(matches_dict)
        
        if not df_live_table.empty:
            df_live_table['logo_url'] = df_live_table['klub'].apply(get_club_logo_url)
            
            st.dataframe(
                df_live_table,
                use_container_width=True, hide_index=True,
                column_config={
                    "logo_url": st.column_config.ImageColumn("Herb", width="small"),
                    "bilans": st.column_config.ProgressColumn("Bilans", min_value=-20, max_value=50, format="%d"),
                    "Miejsce": st.column_config.NumberColumn("#", format="%d"),
                    "forma": st.column_config.TextColumn("Forma (ost. 5)")
                },
                column_order=['Miejsce', 'logo_url', 'klub', 'mecze', 'punkty', 'strzelone', 'stracone', 'bilans', 'wygrane', 'remisy', 'porażki', 'forma']
            )
        else:
            st.info("Brak rozegranych meczów.")

    elif page == "📅 Terminarz":
        st.title("Terminarz i Wyniki")
        
        # Konwersja słownika meczów na listę i sortowanie
        all_matches_list = list(matches_dict.values())
        df_sched = pd.DataFrame(all_matches_list)
        
        if not df_sched.empty:
            df_sched = df_sched.sort_values('Kolejka')
            rounds = sorted(df_sched['Kolejka'].unique())
            sel_round = st.selectbox("Wybierz kolejkę", rounds)
            
            # Filtrowanie kolejki
            round_matches = df_sched[df_sched['Kolejka'] == sel_round]
            
            for _, row in round_matches.iterrows():
                h, g = row['Gospodarze'], row['Goście']
                res = row['Wynik']
                # Joinowanie listy strzelców
                scorers_h = ", ".join(row['Strzelcy_H'])
                scorers_a = ", ".join(row['Strzelcy_A'])
                
                logo_h = get_club_logo_url(h)
                logo_a = get_club_logo_url(g)

                with st.container():
                    # Layout: Gospodarz (Strzelcy) - Wynik - (Strzelcy) Gość
                    col_h_img, col_h_txt, col_res, col_a_txt, col_a_img = st.columns([0.5, 3, 1, 3, 0.5])
                    
                    with col_h_img: 
                        if logo_h: st.image(logo_h, width=50)
                    with col_h_txt:
                        st.markdown(f"<div style='text-align:right; font-weight:bold; font-size:1.1em'>{h}</div>", unsafe_allow_html=True)
                        if scorers_h:
                            st.markdown(f"<div style='text-align:right; font-size:0.8em; color:gray'>⚽ {scorers_h}</div>", unsafe_allow_html=True)
                    
                    with col_res:
                        bg_color = "#e0e0e0" if res == "-" else "#a3ffa3"
                        st.markdown(f"""
                        <div style='background-color:{bg_color}; border-radius:8px; text-align:center; padding:5px; font-weight:bold; color:black; font-size:1.2em'>
                        {res}
                        </div>""", unsafe_allow_html=True)
                        
                    with col_a_txt:
                        st.markdown(f"<div style='text-align:left; font-weight:bold; font-size:1.1em'>{g}</div>", unsafe_allow_html=True)
                        if scorers_a:
                            st.markdown(f"<div style='text-align:left; font-size:0.8em; color:gray'>⚽ {scorers_a}</div>", unsafe_allow_html=True)
                    
                    with col_a_img:
                        if logo_a: st.image(logo_a, width=50)

                    st.divider()
        else:
            st.info("Brak danych w terminarzu.")

    elif page == "🎯 Strzelcy":
        st.title("Najlepsi Strzelcy")
        if 'Strzelcy' in data_sheets:
            df_s = data_sheets['Strzelcy']
            df_s.columns = [str(c).lower().strip() for c in df_s.columns]
            if 'kraj' in df_s.columns: df_s['flaga_url'] = df_s['kraj'].apply(get_flag_url)
            
            cols_to_show = []
            if 'flaga_url' in df_s.columns: cols_to_show.append('flaga_url')
            cols_to_show.extend([c for c in df_s.columns if c not in ['flaga_url', 'kraj']])
            
            st.dataframe(
                df_s[cols_to_show], 
                use_container_width=True, hide_index=True,
                column_config={
                    "flaga_url": st.column_config.ImageColumn("Kraj", width="small"),
                    "gole": st.column_config.ProgressColumn("Gole", format="%d", min_value=0, max_value=25)
                }
            )
        else:
            st.warning("Brak zakładki 'Strzelcy'.")

    elif page == "⚽ Drużyny":
        st.title("Statystyki Drużyn")
        selected_team = st.sidebar.selectbox("Wybierz drużynę", team_names)
        
        if selected_team:
            df_p, df_s, df_m = process_team_sheet(data_sheets[selected_team], selected_team)
            
            # Pobierz statystyki z tabeli (już obliczone)
            team_stats = None
            full_table = calculate_table_from_matches(matches_dict)
            if not full_table.empty:
                row_stats = full_table[full_table['klub'] == selected_team]
                if not row_stats.empty:
                    team_stats = row_stats.iloc[0]

            # HEADER
            c1, c2 = st.columns([1, 5])
            with c1:
                if get_club_logo_url(selected_team): st.image(get_club_logo_url(selected_team), width=100)
            with c2:
                st.header(selected_team)
                if team_stats is not None:
                    st.caption(f"Miejsce: {team_stats['Miejsce']} | Pkt: {team_stats['punkty']} | Bramki: {team_stats['strzelone']}:{team_stats['stracone']}")

            tab1, tab2, tab3 = st.tabs(["📊 Wykresy i Bilans", "👥 Kadra", "📅 Mecze"])
            
            with tab1:
                # 1. Bilans DOM / WYJAZD
                if team_stats is not None:
                    st.subheader("Bilans meczów")
                    k1, k2, k3 = st.columns(3)
                    k1.metric("Łącznie", f"{team_stats['wygrane']}W - {team_stats['remisy']}R - {team_stats['porażki']}P")
                    k2.metric("Dom", f"{team_stats['dom_w']}W - {team_stats['dom_r']}R - {team_stats['dom_p']}P")
                    k3.metric("Wyjazd", f"{team_stats['wyj_w']}W - {team_stats['wyj_r']}R - {team_stats['wyj_p']}P")
                    
                    st.markdown("---")

                # 2. Wykresy zawodników
                if not df_p.empty:
                    c1, c2 = st.columns(2)
                    with c1:
                        if 'gole' in df_p.columns:
                            scorers = df_p[df_p['gole'] > 0].sort_values('gole', ascending=True)
                            if not scorers.empty:
                                fig = px.bar(scorers, x='gole', y='imię i nazwisko', orientation='h', title="Strzelcy", color='gole')
                                fig.update_layout(xaxis_title=None, yaxis_title=None)
                                st.plotly_chart(fig, use_container_width=True)
                    with c2:
                        if 'minuty' in df_p.columns:
                            mins = df_p.nlargest(10, 'minuty').sort_values('minuty', ascending=True)
                            fig = px.bar(mins, x='minuty', y='imię i nazwisko', orientation='h', title="Minuty", color='minuty')
                            fig.update_layout(xaxis_title=None, yaxis_title=None)
                            st.plotly_chart(fig, use_container_width=True)

            with tab2:
                if not df_p.empty:
                    cols = ['numer', 'flaga_url', 'imię i nazwisko', 'pozycja', 'wiek', 'mecze', 'minuty', 'gole', 'asysty']
                    visible = [c for c in cols if c in df_p.columns]
                    st.dataframe(df_p[visible], use_container_width=True, hide_index=True, column_config={"flaga_url": st.column_config.ImageColumn("", width="small")})

            with tab3:
                if not df_m.empty and 'wynik' in df_m.columns:
                    st.dataframe(df_m, use_container_width=True, hide_index=True)
else:
    st.error(f"Nie znaleziono pliku {EXCEL_FILE}.")
