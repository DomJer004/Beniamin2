import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

st.set_page_config(page_title="Liga Mistrzów 25/26", layout="wide", page_icon="⚽")

EXCEL_FILE = "Liga Mistrzów 25_26.xlsx"

# --- 1. HERBY KLUBÓW (WIKIMEDIA - KOMPLET) ---
CLUB_LOGOS = {
    # Anglia
    "Arsenal": "https://upload.wikimedia.org/wikipedia/en/5/53/Arsenal_FC.svg",
    "Aston Villa": "https://upload.wikimedia.org/wikipedia/en/9/9f/Aston_Villa_logo.svg",
    "Liverpool": "https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg",
    "Manchester City": "https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
    "City": "https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
    "Chelsea": "https://upload.wikimedia.org/wikipedia/en/c/cc/Chelsea_FC.svg",
    "Tottenham Hotspur": "https://upload.wikimedia.org/wikipedia/en/b/b4/Tottenham_Hotspur.svg",
    "Tottenham": "https://upload.wikimedia.org/wikipedia/en/b/b4/Tottenham_Hotspur.svg",
    "Newcastle United": "https://upload.wikimedia.org/wikipedia/en/5/56/Newcastle_United_Logo.svg",
    "Newcastle": "https://upload.wikimedia.org/wikipedia/en/5/56/Newcastle_United_Logo.svg",
    
    # Hiszpania
    "Real Madryt": "https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg",
    "Real": "https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg",
    "Barcelona": "https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg",
    "Barca": "https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg",
    "Atlético Madryt": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "Atletico Madryt": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "Atlético": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "Atletico": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "Girona": "https://upload.wikimedia.org/wikipedia/en/9/90/Girona_FC_Crest.svg",
    "Athletic Bilbao": "https://upload.wikimedia.org/wikipedia/en/9/98/Club_Athletic_Bilbao_logo.svg",
    "Bilbao": "https://upload.wikimedia.org/wikipedia/en/9/98/Club_Athletic_Bilbao_logo.svg",
    "Villarreal": "https://upload.wikimedia.org/wikipedia/en/7/70/Villarreal_CF_logo.svg",
    
    # Niemcy
    "Bayern Monachium": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_München_logo_%282017%29.svg",
    "Bayern": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_München_logo_%282017%29.svg",
    "Borussia Dortmund": "https://upload.wikimedia.org/wikipedia/commons/6/67/Borussia_Dortmund_logo.svg",
    "Borussia": "https://upload.wikimedia.org/wikipedia/commons/6/67/Borussia_Dortmund_logo.svg",
    "Bayer Leverkusen": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
    "Leverkusen": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
    "RB Leipzig": "https://upload.wikimedia.org/wikipedia/en/0/04/RB_Leipzig_2014_logo.svg",
    "Stuttgart": "https://upload.wikimedia.org/wikipedia/commons/e/eb/VfB_Stuttgart_1893_Logo.svg",
    "Eintracht Frankfurt": "https://upload.wikimedia.org/wikipedia/commons/0/04/Eintracht_Frankfurt_Logo.svg",
    "Frankfurt": "https://upload.wikimedia.org/wikipedia/commons/0/04/Eintracht_Frankfurt_Logo.svg",
    
    # Włochy
    "Inter Mediolan": "https://upload.wikimedia.org/wikipedia/commons/0/05/FC_Internazionale_Milano_2021.svg",
    "Inter": "https://upload.wikimedia.org/wikipedia/commons/0/05/FC_Internazionale_Milano_2021.svg",
    "AC Milan": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Logo_of_AC_Milan.svg",
    "Milan": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Logo_of_AC_Milan.svg",
    "Juventus": "https://upload.wikimedia.org/wikipedia/commons/5/51/Juventus_FC_2017_icon_%28black%29.svg",
    "Atalanta": "https://upload.wikimedia.org/wikipedia/en/6/66/AtalantaBC.svg",
    "Bologna": "https://upload.wikimedia.org/wikipedia/en/5/5b/Bologna_F.C._1909_logo.svg",
    "Napoli": "https://upload.wikimedia.org/wikipedia/commons/2/2d/SSC_Neapel.svg",
    
    # Francja
    "Paris Saint-Germain": "https://upload.wikimedia.org/wikipedia/en/a/a7/Paris_Saint-Germain_F.C..svg",
    "PSG": "https://upload.wikimedia.org/wikipedia/en/a/a7/Paris_Saint-Germain_F.C..svg",
    "Monaco": "https://upload.wikimedia.org/wikipedia/en/b/ba/AS_Monaco_FC.svg",
    "Brest": "https://upload.wikimedia.org/wikipedia/en/0/05/Stade_Brestois_29_logo.svg",
    "Lille": "https://upload.wikimedia.org/wikipedia/en/6/6f/Lille_OSC_2018_logo.svg",
    "Olympique Marsylia": "https://upload.wikimedia.org/wikipedia/commons/d/d8/Olympique_Marseille_logo.svg",
    "Marsylia": "https://upload.wikimedia.org/wikipedia/commons/d/d8/Olympique_Marseille_logo.svg",
    
    # Portugalia
    "Sporting CP": "https://upload.wikimedia.org/wikipedia/en/e/e1/Sporting_Clube_de_Portugal_%28Complex%29.svg",
    "Sporting": "https://upload.wikimedia.org/wikipedia/en/e/e1/Sporting_Clube_de_Portugal_%28Complex%29.svg",
    "Benfica": "https://upload.wikimedia.org/wikipedia/en/a/a2/SL_Benfica_logo.svg",
    "FC Porto": "https://upload.wikimedia.org/wikipedia/en/f/f1/FC_Porto.svg",
    
    # Holandia
    "PSV Eindhoven": "https://upload.wikimedia.org/wikipedia/en/0/05/PSV_Eindhoven.svg",
    "PSV": "https://upload.wikimedia.org/wikipedia/en/0/05/PSV_Eindhoven.svg",
    "Feyenoord": "https://upload.wikimedia.org/wikipedia/en/e/e3/Feyenoord_logo.svg",
    "Ajax": "https://upload.wikimedia.org/wikipedia/en/7/79/Ajax_Amsterdam.svg",
    
    # Belgia
    "Club Brugge": "https://upload.wikimedia.org/wikipedia/en/d/d0/Club_Brugge_KV_logo.svg",
    "Brugge": "https://upload.wikimedia.org/wikipedia/en/d/d0/Club_Brugge_KV_logo.svg",
    "Union Saint-Gilloise": "https://upload.wikimedia.org/wikipedia/en/6/64/Royale_Union_Saint-Gilloise_Logo.svg",
    "USG": "https://upload.wikimedia.org/wikipedia/en/6/64/Royale_Union_Saint-Gilloise_Logo.svg",
    
    # Pozostałe
    "Celtic": "https://upload.wikimedia.org/wikipedia/en/3/35/Celtic_FC.svg",
    "Sturm Graz": "https://upload.wikimedia.org/wikipedia/commons/c/cc/SK_Sturm_Graz_Logo.svg",
    "RB Salzburg": "https://upload.wikimedia.org/wikipedia/en/7/77/FC_Red_Bull_Salzburg_logo.svg",
    "Szachtar Donieck": "https://upload.wikimedia.org/wikipedia/en/a/a1/FC_Shakhtar_Donetsk.svg",
    "Dinamo Zagrzeb": "https://upload.wikimedia.org/wikipedia/en/f/f6/NK_Dinamo_Zagreb.svg",
    "Crvena Zvezda": "https://upload.wikimedia.org/wikipedia/commons/2/2a/Red_Star_Belgrade_logo.svg",
    "Young Boys": "https://upload.wikimedia.org/wikipedia/en/6/6b/BSC_Young_Boys_logo.svg",
    "Sparta Praga": "https://upload.wikimedia.org/wikipedia/en/3/39/AC_Sparta_Praha_logo.svg",
    "Slavia Praga": "https://upload.wikimedia.org/wikipedia/en/3/36/SK_Slavia_Praha_logo.svg",
    "Slavia": "https://upload.wikimedia.org/wikipedia/en/3/36/SK_Slavia_Praha_logo.svg",
    "Slovan Bratysława": "https://upload.wikimedia.org/wikipedia/en/8/8b/Slovan_Bratislava_logo.svg",
    "Galatasaray": "https://upload.wikimedia.org/wikipedia/en/3/31/Galatasaray_Star_Logo.svg",
    "Kopenhaga": "https://upload.wikimedia.org/wikipedia/en/9/93/FC_København.svg",
    "FC Kopenhaga": "https://upload.wikimedia.org/wikipedia/en/9/93/FC_København.svg",
    "Bodo/Glimt": "https://upload.wikimedia.org/wikipedia/en/2/22/FK_Bodø_Glimt.svg",
    "Bodø/Glimt": "https://upload.wikimedia.org/wikipedia/en/2/22/FK_Bodø_Glimt.svg",
    "Bodo": "https://upload.wikimedia.org/wikipedia/en/2/22/FK_Bodø_Glimt.svg",
    "Olympiacos": "https://upload.wikimedia.org/wikipedia/en/f/f1/Olympiacos_FC_logo.svg",
    "Karabach": "https://upload.wikimedia.org/wikipedia/en/9/9b/Qarabağ_FK_logo.svg",
    "Pafos": "https://upload.wikimedia.org/wikipedia/en/d/d5/Pafos_FC_logo.svg",
    "Kairat Ałmaty": "https://upload.wikimedia.org/wikipedia/en/6/6e/FC_Kairat_Logo.svg",
    "Kairat": "https://upload.wikimedia.org/wikipedia/en/6/6e/FC_Kairat_Logo.svg"
}

# --- 2. KODY FLAG (Dla API FlagCDN) ---
COUNTRY_CODES = {
    "Anglia": "gb-eng", "Szkocja": "gb-sct", "Walia": "gb-wls", "Irlandia Północna": "gb-nir", "Kanada": "ca",
    "Polska": "pl", "Hiszpania": "es", "Niemcy": "de", "Włochy": "it", "Francja": "fr", "Portugalia": "pt", "Holandia": "nl", 
    "Belgia": "be", "Chorwacja": "hr", "Dania": "dk", "Szwecja": "se", "Norwegia": "no", "Irlandia": "ie", "Czechy": "cz", 
    "Słowacja": "sk", "Ukraina": "ua", "Turcja": "tr", "Grecja": "gr", "Szwajcaria": "ch", "Austria": "at", "Węgry": "hu", 
    "Rumunia": "ro", "Bułgaria": "bg", "Finlandia": "fi", "Islandia": "is", "Słowenia": "si", "Serbia": "rs", 
    "Bośnia i Hercegowina": "ba", "Gruzja": "ge", "Armenia": "am", "Azerbejdżan": "az", "Kazachstan": "kz", "Cypr": "cy", 
    "Albania": "al", "Kosowo": "xk", "Czarnogóra": "me", "Macedonia Północna": "mk", "Rosja": "ru", "Mołdawia": "md",
    "Brazylia": "br", "Argentyna": "ar", "Urugwaj": "uy", "Kolumbia": "co", "Chile": "cl", "Ekwador": "ec", "Paragwaj": "py", 
    "Wenezuela": "ve", "Peru": "pe", "USA": "us", "Meksyk": "mx", "Surinam": "sr", "Jamajka": "jm", "Gwadelupa": "gp", "Curaçao": "cw",
    "Maroko": "ma", "Senegal": "sn", "Egipt": "eg", "Nigeria": "ng", "Kamerun": "cm", "Ghana": "gh", "Wybrzeże Kości Słoniowej": "ci",
    "Algieria": "dz", "Tunezja": "tn", "Mali": "ml", "Gabon": "ga", "Gambia": "gm", "Kongo": "cg", "Demokratyczna Republika Konga": "cd",
    "Demokratyczne Republika Konga": "cd", "Gwinea": "gn", "Gwinea Równikowa": "gq", "Gwinea Bissau": "gw", "Burkina Faso": "bf", 
    "RPA": "za", "Zimbabwe": "zw", "Republika Zielonego Przylądka": "cv", "Mozambik": "mz", "Libia": "ly",
    "Japonia": "jp", "Korea Południowa": "kr", "Chiny": "cn", "Australia": "au", "Iran": "ir", "Izrael": "il", "Syria": "sy"
}

def get_flag_url(nationality_str):
    if not isinstance(nationality_str, str) or not nationality_str.strip(): return None
    first_country = nationality_str.replace("/", ",").split(",")[0].strip()
    if "Konaga" in first_country or "Konga" in first_country: first_country = "Demokratyczna Republika Konga"
    if "Niemcu" in first_country: first_country = "Niemcy"
    code = COUNTRY_CODES.get(first_country)
    return f"https://flagcdn.com/w40/{code}.png" if code else None

def get_club_logo_url(club_name):
    if not isinstance(club_name, str): return None
    # Normalizacja nazwy do klucza słownika
    clean_name = club_name.strip()
    return CLUB_LOGOS.get(clean_name, None)

def repair_excel_date_score(value):
    """Naprawia wynik jeśli Excel zamienił go na datę."""
    if pd.isna(value): return None
    val_str = str(value).strip()
    if "-" in val_str and len(val_str) < 6: return val_str
    try:
        dt = pd.to_datetime(value, errors='coerce')
        if not pd.isna(dt):
            # Zakładamy format Dzień-Miesiąc
            return f"{dt.day}-{dt.month}"
    except:
        pass
    return val_str

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
        if pd.isna(c) or str(c).strip() == "" or str(c).lower() == "nan": continue
        col_str = str(c).strip()
        seen[col_str] = seen.get(col_str, 0) + 1
        new_columns.append(f"{col_str}_{seen[col_str]}" if seen[col_str] > 1 else col_str)
        indices.append(i)
    
    matches = df.iloc[start_row_idx+1:, indices].copy()
    matches.columns = new_columns
    
    # NAPRAWA WYNIKÓW
    if 'wynik' in matches.columns:
        matches['wynik'] = matches['wynik'].apply(repair_excel_date_score)
        
    return matches

def process_team_sheet(df, team_name):
    try:
        match_split = df.index[df.iloc[:, 0].astype(str).str.lower() == 'kolejka'].tolist()
        match_idx = match_split[0] if match_split else len(df)
        df_top = df.iloc[:match_idx].copy()
        
        # Szukamy podziału "funkcja" lub "rola"
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
            
            # Normalizacja kolumny funkcji
            if 'rola' in df_staff.columns: df_staff.rename(columns={'rola': 'funkcja'}, inplace=True)
            
            # Czyszczenie sztabu
            if 'funkcja' in df_staff.columns: df_staff = df_staff.dropna(subset=['funkcja'])
            if 'imię i nazwisko' in df_staff.columns: df_staff = df_staff.dropna(subset=['imię i nazwisko'])
                
        else:
            df_players = df_top.copy()
            df_staff = pd.DataFrame()

        # Czyszczenie piłkarzy
        if 'imię i nazwisko' in df_players.columns: df_players = df_players.dropna(subset=['imię i nazwisko'])
        else: df_players = df_players.dropna(how='all')

        if not df_players.empty:
            df_players.columns = [str(c).lower().strip() for c in df_players.columns]
            df_players.rename(columns={'t': 'numer', 'nr': 'numer'}, inplace=True)
            
            cols_num = ['mecze', 'minuty', 'gole', 'asysty', 'żółte kartki', 'kanadyjka', 'wiek']
            for col in cols_num:
                if col in df_players.columns:
                    df_players[col] = pd.to_numeric(df_players[col], errors='coerce').fillna(0).astype(int)
            
            if 'narodowość' in df_players.columns:
                df_players['flaga_url'] = df_players['narodowość'].apply(get_flag_url)

        if not df_staff.empty:
            if 'narodowość' in df_staff.columns:
                df_staff['flaga_url'] = df_staff['narodowość'].apply(get_flag_url)

        df_matches = clean_matches_table(df, match_idx)
        return df_players, df_staff, df_matches

    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- FUNKCJA OBLICZANIA TABELI NA ŻYWO ---
def calculate_live_table(data_sheets):
    """Przelicza tabelę ligową na podstawie wyników w arkuszach."""
    stats = {} # {TeamName: {M, Pkt, G+, G-, W, R, P}}
    
    ignore = ['Tabela', 'Strzelcy', 'Legenda', 'Info']
    processed_matches = set() # Żeby nie liczyć podwójnie
    
    for sheet_name, df in data_sheets.items():
        if sheet_name in ignore: continue
        
        _, _, df_m = process_team_sheet(df, sheet_name)
        
        if not df_m.empty and 'wynik' in df_m.columns and 'gospodarze' in df_m.columns:
            for _, row in df_m.iterrows():
                host = str(row['gospodarze']).strip()
                guest = str(row['goście']).strip()
                wynik = str(row['wynik']).strip()
                kolejka = str(row['kolejka']).strip()
                
                # Unikalne ID meczu
                match_id = "-".join(sorted([host, guest])) + f"-k{kolejka}"
                if match_id in processed_matches: continue
                
                # Inicjalizacja drużyn w stats
                if host not in stats: stats[host] = {'M':0, 'Pkt':0, 'BZ':0, 'BS':0, 'W':0, 'R':0, 'P':0}
                if guest not in stats: stats[guest] = {'M':0, 'Pkt':0, 'BZ':0, 'BS':0, 'W':0, 'R':0, 'P':0}
                
                # Parsowanie wyniku
                if '-' in wynik and wynik.replace('-','').isdigit():
                    processed_matches.add(match_id)
                    h_goals, a_goals = map(int, wynik.split('-'))
                    
                    # Gospodarz
                    stats[host]['M'] += 1
                    stats[host]['BZ'] += h_goals
                    stats[host]['BS'] += a_goals
                    
                    # Gość
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

    # Konwersja do DataFrame
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

# --- APP START ---

data_sheets = load_all_data(EXCEL_FILE)

if data_sheets:
    st.sidebar.title("Menu")
    sheet_names = list(data_sheets.keys())
    special_sheets = ['Tabela', 'Strzelcy', 'Legenda', 'Info']
    team_names = sorted([n for n in sheet_names if n not in special_sheets])
    
    page = st.sidebar.radio("Wybierz widok", ["🏆 Tabela Ligowa", "📅 Terminarz", "🎯 Strzelcy", "⚽ Drużyny"])
    
    # --- 1. TABELA LIGOWA (DYNAMICZNA) ---
    if page == "🏆 Tabela Ligowa":
        st.title("Tabela Ligi Mistrzów 25/26 (Live)")
        
        # Obliczamy tabelę na podstawie meczów
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
            st.info("Brak rozegranych meczów do wyświetlenia tabeli.")

    # --- 2. TERMINARZ Z STRZELCAMI ---
    elif page == "📅 Terminarz":
        st.title("Terminarz i Wyniki")
        
        # Zbieramy wszystkie mecze
        all_matches = []
        processed_ids = set()
        
        for name in team_names:
            _, _, df_m = process_team_sheet(data_sheets[name], name)
            if not df_m.empty and 'wynik' in df_m.columns:
                # Szukamy kolumn ze strzelcami (zawierają 'gole dla' lub 'strzelcy')
                scorer_cols = [c for c in df_m.columns if 'gole dla' in str(c).lower() or 'strzelcy' in str(c).lower()]
                
                for _, row in df_m.iterrows():
                    h, g = str(row['gospodarze']).strip(), str(row['goście']).strip()
                    k = row['kolejka']
                    mid = "-".join(sorted([h, g])) + f"-k{k}"
                    
                    if mid in processed_ids: continue
                    processed_ids.add(mid)
                    
                    # Pobieranie strzelców (tekst)
                    scorers_txt = ""
                    for sc in scorer_cols:
                        if pd.notna(row[sc]):
                            scorers_txt += str(row[sc]) + " "
                    
                    res = row['wynik']
                    if pd.isna(res) or str(res).strip() == "" or str(res).lower() == "nan":
                        res_display = "Mecz nieuzupełniony"
                    else:
                        res_display = str(res)

                    all_matches.append({
                        "Kolejka": int(k) if str(k).isdigit() else 0,
                        "Gospodarze": h, "Goście": g, "Wynik": res_display,
                        "Strzelcy": scorers_txt.strip(),
                        "Logo_H": get_club_logo_url(h), "Logo_A": get_club_logo_url(g)
                    })
        
        df_sched = pd.DataFrame(all_matches).sort_values('Kolejka')
        
        if not df_sched.empty:
            rounds = sorted(df_sched['Kolejka'].unique())
            sel_round = st.selectbox("Wybierz kolejkę", rounds)
            
            for _, row in df_sched[df_sched['Kolejka'] == sel_round].iterrows():
                with st.container():
                    c1, c2, c3, c4, c5 = st.columns([1, 3, 2, 3, 1])
                    with c1: 
                        if row['Logo_H']: st.image(row['Logo_H'], width=40)
                    with c2: st.markdown(f"**{row['Gospodarze']}**")
                    with c3: 
                        st.markdown(f"<h4 style='text-align:center'>{row['Wynik']}</h4>", unsafe_allow_html=True)
                    with c4: st.markdown(f"**{row['Goście']}**")
                    with c5: 
                        if row['Logo_A']: st.image(row['Logo_A'], width=40)
                    
                    if row['Strzelcy']:
                        st.caption(f"⚽ {row['Strzelcy']}")
                    st.divider()

    # --- 3. STRZELCY ---
    elif page == "🎯 Strzelcy":
        st.title("Najlepsi Strzelcy")
        if 'Strzelcy' in data_sheets:
            df_s = data_sheets['Strzelcy']
            if 'kraj' in df_s.columns: df_s['flaga_url'] = df_s['kraj'].apply(get_flag_url)
            if 'data urodzenia' in df_s.columns:
                df_s['data urodzenia'] = pd.to_datetime(df_s['data urodzenia'], errors='coerce').dt.date
            
            st.dataframe(
                df_s, use_container_width=True, hide_index=True,
                column_config={
                    "flaga_url": st.column_config.ImageColumn("Kraj", width="small"),
                    "data urodzenia": st.column_config.DateColumn("Data ur.", format="DD.MM.YYYY")
                }
            )

    # --- 4. DRUŻYNY ---
    elif page == "⚽ Drużyny":
        st.title("Statystyki Drużyn")
        selected_team = st.sidebar.selectbox("Wybierz drużynę", team_names)
        
        if selected_team:
            df_p, df_s, df_m = process_team_sheet(data_sheets[selected_team], selected_team)
            
            # HEADER Z LOGO
            ch1, ch2 = st.columns([1, 6])
            with ch1:
                logo = get_club_logo_url(selected_team)
                if logo: st.image(logo, width=80)
            with ch2:
                st.header(f"Raport: {selected_team}")
            
            # KPI (Licznik meczów tylko rozegranych)
            matches_played = 0
            if not df_m.empty and 'wynik' in df_m.columns:
                matches_played = df_m['wynik'].apply(lambda x: 1 if pd.notna(x) and str(x).strip() != '' else 0).sum()
                
            goals = df_p['gole'].sum() if not df_p.empty and 'gole' in df_p.columns else 0
            
            k1, k2 = st.columns(2)
            k1.metric("Gole Zespołu", goals)
            k2.metric("Rozegrane Mecze", matches_played)
            
            tab1, tab2, tab3 = st.tabs(["Kadra", "Terminarz", "Statystyki"])
            
            with tab1:
                st.subheader("Zawodnicy")
                if not df_p.empty:
                    cols_p = ['numer', 'flaga_url', 'imię i nazwisko', 'pozycja', 'narodowość', 'wiek', 'mecze', 'gole', 'asysty', 'kanadyjka']
                    final_p = [c for c in cols_p if c in df_p.columns]
                    max_g = df_p['gole'].max() if 'gole' in df_p.columns else 10
                    
                    st.dataframe(
                        df_p[final_p], use_container_width=True, hide_index=True,
                        column_config={
                            "flaga_url": st.column_config.ImageColumn("Kraj", width="small"),
                            "gole": st.column_config.ProgressColumn("Gole", format="%d", min_value=0, max_value=int(max_g) if max_g > 0 else 1),
                            "numer": st.column_config.NumberColumn("#", format="%d")
                        }
                    )
                
                if not df_s.empty:
                    st.markdown("---")
                    st.subheader("Sztab")
                    cols_s = ['flaga_url', 'imię i nazwisko', 'funkcja', 'narodowość', 'wiek']
                    final_s = [c for c in cols_s if c in df_s.columns]
                    st.dataframe(
                        df_s[final_s], use_container_width=True, hide_index=True,
                        column_config={"flaga_url": st.column_config.ImageColumn("Kraj", width="small")}
                    )

            with tab2:
                if not df_m.empty and 'wynik' in df_m.columns:
                    # Kolorowanie
                    def style_res(row):
                        res = str(row['wynik'])
                        if not res or res == 'nan' or res == 'None': return ""
                        try:
                            if '-' in res:
                                h, a = map(int, res.split('-'))
                                # Prosta detekcja po nazwie
                                if selected_team in str(row['gospodarze']):
                                    if h > a: return "color: green"
                                    if h < a: return "color: red"
                                    return "color: #b58900"
                                elif selected_team in str(row['goście']):
                                    if a > h: return "color: green"
                                    if a < h: return "color: red"
                                    return "color: #b58900"
                        except: pass
                        return ""
                        
                    # Wyświetlanie "Mecz nieuzupełniony"
                    df_show = df_m.copy()
                    df_show['wynik'] = df_show['wynik'].apply(lambda x: x if pd.notna(x) and str(x).strip() != "" else "Mecz nieuzupełniony")
                    
                    st.dataframe(
                        df_show.style.apply(lambda x: [style_res(x) if col == 'wynik' else '' for col in x.index], axis=1),
                        use_container_width=True, hide_index=True
                    )
                else:
                    st.info("Brak meczów.")

            with tab3:
                if not df_p.empty:
                    c1, c2 = st.columns(2)
                    with c1:
                        if 'minuty' in df_p.columns:
                            top = df_p.nlargest(15, 'minuty').sort_values('minuty')
                            st.plotly_chart(px.bar(top, x='minuty', y='imię i nazwisko', orientation='h', title="Minuty", text='minuty'), use_container_width=True)
                    with c2:
                        if 'gole' in df_p.columns:
                            sc = df_p[df_p['gole']>0].sort_values('gole')
                            if not sc.empty:
                                st.plotly_chart(px.bar(sc, x='gole', y='imię i nazwisko', orientation='h', title="Gole", text='gole', color_discrete_sequence=['red']), use_container_width=True)
