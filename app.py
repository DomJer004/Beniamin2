import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Liga Mistrzów 25/26", layout="wide", page_icon="⚽")

EXCEL_FILE = "Liga Mistrzów 25_26.xlsx"

# --- 1. HERBY KLUBÓW (WIKIMEDIA) ---
CLUB_LOGOS = {
    "Arsenal": "https://upload.wikimedia.org/wikipedia/en/5/53/Arsenal_FC.svg",
    "Aston Villa": "https://upload.wikimedia.org/wikipedia/en/9/9f/Aston_Villa_logo.svg",
    "Liverpool": "https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg",
    "Manchester City": "https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
    "Chelsea": "https://upload.wikimedia.org/wikipedia/en/c/cc/Chelsea_FC.svg",
    "Tottenham Hotspur": "https://upload.wikimedia.org/wikipedia/en/b/b4/Tottenham_Hotspur.svg",
    "Newcastle United": "https://upload.wikimedia.org/wikipedia/en/5/56/Newcastle_United_Logo.svg",
    "Newcastle": "https://upload.wikimedia.org/wikipedia/en/5/56/Newcastle_United_Logo.svg",
    
    "Real Madryt": "https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg",
    "Barcelona": "https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg",
    "Atlético Madryt": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "Atletico Madryt": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "Girona": "https://upload.wikimedia.org/wikipedia/en/9/90/Girona_FC_Crest.svg",
    "Athletic Bilbao": "https://upload.wikimedia.org/wikipedia/en/9/98/Club_Athletic_Bilbao_logo.svg",
    "Villarreal": "https://upload.wikimedia.org/wikipedia/en/7/70/Villarreal_CF_logo.svg",
    
    "Bayern Monachium": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_München_logo_%282017%29.svg",
    "Borussia Dortmund": "https://upload.wikimedia.org/wikipedia/commons/6/67/Borussia_Dortmund_logo.svg",
    "Bayer Leverkusen": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
    "RB Leipzig": "https://upload.wikimedia.org/wikipedia/en/0/04/RB_Leipzig_2014_logo.svg",
    "Stuttgart": "https://upload.wikimedia.org/wikipedia/commons/e/eb/VfB_Stuttgart_1893_Logo.svg",
    "Eintracht Frankfurt": "https://upload.wikimedia.org/wikipedia/commons/0/04/Eintracht_Frankfurt_Logo.svg",
    
    "Inter Mediolan": "https://upload.wikimedia.org/wikipedia/commons/0/05/FC_Internazionale_Milano_2021.svg",
    "AC Milan": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Logo_of_AC_Milan.svg",
    "Juventus": "https://upload.wikimedia.org/wikipedia/commons/5/51/Juventus_FC_2017_icon_%28black%29.svg",
    "Atalanta": "https://upload.wikimedia.org/wikipedia/en/6/66/AtalantaBC.svg",
    "Bologna": "https://upload.wikimedia.org/wikipedia/en/5/5b/Bologna_F.C._1909_logo.svg",
    "Napoli": "https://upload.wikimedia.org/wikipedia/commons/2/2d/SSC_Neapel.svg",
    
    "Paris Saint-Germain": "https://upload.wikimedia.org/wikipedia/en/a/a7/Paris_Saint-Germain_F.C..svg",
    "PSG": "https://upload.wikimedia.org/wikipedia/en/a/a7/Paris_Saint-Germain_F.C..svg",
    "Monaco": "https://upload.wikimedia.org/wikipedia/en/b/ba/AS_Monaco_FC.svg",
    "Brest": "https://upload.wikimedia.org/wikipedia/en/0/05/Stade_Brestois_29_logo.svg",
    "Lille": "https://upload.wikimedia.org/wikipedia/en/6/6f/Lille_OSC_2018_logo.svg",
    "Olympique Marsylia": "https://upload.wikimedia.org/wikipedia/commons/d/d8/Olympique_Marseille_logo.svg",
    "Marsylia": "https://upload.wikimedia.org/wikipedia/commons/d/d8/Olympique_Marseille_logo.svg",
    
    "Sporting CP": "https://upload.wikimedia.org/wikipedia/en/e/e1/Sporting_Clube_de_Portugal_%28Complex%29.svg",
    "Benfica": "https://upload.wikimedia.org/wikipedia/en/a/a2/SL_Benfica_logo.svg",
    
    "PSV Eindhoven": "https://upload.wikimedia.org/wikipedia/en/0/05/PSV_Eindhoven.svg",
    "PSV": "https://upload.wikimedia.org/wikipedia/en/0/05/PSV_Eindhoven.svg",
    "Feyenoord": "https://upload.wikimedia.org/wikipedia/en/e/e3/Feyenoord_logo.svg",
    "Ajax": "https://upload.wikimedia.org/wikipedia/en/7/79/Ajax_Amsterdam.svg",
    
    "Club Brugge": "https://upload.wikimedia.org/wikipedia/en/d/d0/Club_Brugge_KV_logo.svg",
    "Brugge": "https://upload.wikimedia.org/wikipedia/en/d/d0/Club_Brugge_KV_logo.svg",
    "Union Saint-Gilloise": "https://upload.wikimedia.org/wikipedia/en/6/64/Royale_Union_Saint-Gilloise_Logo.svg",
    "USG": "https://upload.wikimedia.org/wikipedia/en/6/64/Royale_Union_Saint-Gilloise_Logo.svg",
    
    "Celtic": "https://upload.wikimedia.org/wikipedia/en/3/35/Celtic_FC.svg",
    "Sturm Graz": "https://upload.wikimedia.org/wikipedia/commons/c/cc/SK_Sturm_Graz_Logo.svg",
    "RB Salzburg": "https://upload.wikimedia.org/wikipedia/en/7/77/FC_Red_Bull_Salzburg_logo.svg",
    "Szachtar Donieck": "https://upload.wikimedia.org/wikipedia/en/a/a1/FC_Shakhtar_Donetsk.svg",
    "Dinamo Zagrzeb": "https://upload.wikimedia.org/wikipedia/en/f/f6/NK_Dinamo_Zagreb.svg",
    "Crvena Zvezda": "https://upload.wikimedia.org/wikipedia/commons/2/2a/Red_Star_Belgrade_logo.svg",
    "Young Boys": "https://upload.wikimedia.org/wikipedia/en/6/6b/BSC_Young_Boys_logo.svg",
    "Sparta Praga": "https://upload.wikimedia.org/wikipedia/en/3/39/AC_Sparta_Praha_logo.svg",
    "Slavia Praga": "https://upload.wikimedia.org/wikipedia/en/3/36/SK_Slavia_Praha_logo.svg",
    "Slovan Bratysława": "https://upload.wikimedia.org/wikipedia/en/8/8b/Slovan_Bratislava_logo.svg",
    "Galatasaray": "https://upload.wikimedia.org/wikipedia/en/3/31/Galatasaray_Star_Logo.svg",
    "Kopenhaga": "https://upload.wikimedia.org/wikipedia/en/9/93/FC_København.svg",
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
    # Regiony UK
    "Anglia": "gb-eng", "Szkocja": "gb-sct", "Walia": "gb-wls", "Irlandia Północna": "gb-nir",
    "Kanada": "ca",
    
    # Europa
    "Polska": "pl", "Hiszpania": "es", "Niemcy": "de", "Włochy": "it",
    "Francja": "fr", "Portugalia": "pt", "Holandia": "nl", "Belgia": "be",
    "Chorwacja": "hr", "Dania": "dk", "Szwecja": "se", "Norwegia": "no",
    "Irlandia": "ie", "Czechy": "cz", "Słowacja": "sk", "Ukraina": "ua",
    "Turcja": "tr", "Grecja": "gr", "Szwajcaria": "ch", "Austria": "at",
    "Węgry": "hu", "Rumunia": "ro", "Bułgaria": "bg", "Finlandia": "fi",
    "Islandia": "is", "Słowenia": "si", "Serbia": "rs", "Bośnia i Hercegowina": "ba",
    "Gruzja": "ge", "Armenia": "am", "Azerbejdżan": "az", "Kazachstan": "kz",
    "Cypr": "cy", "Albania": "al", "Kosowo": "xk", "Czarnogóra": "me",
    "Macedonia Północna": "mk", "Rosja": "ru", "Mołdawia": "md",
    
    # Ameryka
    "Brazylia": "br", "Argentyna": "ar", "Urugwaj": "uy", "Kolumbia": "co",
    "Chile": "cl", "Ekwador": "ec", "Paragwaj": "py", "Wenezuela": "ve",
    "Peru": "pe", "USA": "us", "Meksyk": "mx", "Surinam": "sr",
    "Jamajka": "jm", "Gwadelupa": "gp", "Curaçao": "cw",
    
    # Afryka
    "Maroko": "ma", "Senegal": "sn", "Egipt": "eg", "Nigeria": "ng",
    "Kamerun": "cm", "Ghana": "gh", "Wybrzeże Kości Słoniowej": "ci",
    "Algieria": "dz", "Tunezja": "tn", "Mali": "ml", "Gabon": "ga",
    "Gambia": "gm", "Kongo": "cg", "Demokratyczna Republika Konga": "cd",
    "Demokratyczne Republika Konga": "cd", "Gwinea": "gn", 
    "Gwinea Równikowa": "gq", "Gwinea Bissau": "gw",
    "Burkina Faso": "bf", "RPA": "za", "Zimbabwe": "zw",
    "Republika Zielonego Przylądka": "cv", "Mozambik": "mz", "Libia": "ly",
    
    # Azja
    "Japonia": "jp", "Korea Południowa": "kr", "Chiny": "cn",
    "Australia": "au", "Iran": "ir", "Izrael": "il", "Syria": "sy"
}

def get_flag_url(nationality_str):
    if not isinstance(nationality_str, str) or not nationality_str.strip():
        return None
    first_country = nationality_str.replace("/", ",").split(",")[0].strip()
    if "Konaga" in first_country or "Konga" in first_country: first_country = "Demokratyczna Republika Konga"
    if "Niemcu" in first_country: first_country = "Niemcy"
    
    code = COUNTRY_CODES.get(first_country)
    return f"https://flagcdn.com/w40/{code}.png" if code else None

def get_club_logo_url(club_name):
    if not isinstance(club_name, str):
        return None
    return CLUB_LOGOS.get(club_name.strip(), None)

@st.cache_data
def load_all_data(file_path):
    if not os.path.exists(file_path):
        st.error(f"❌ Nie znaleziono pliku: {file_path}")
        return None
    try:
        return pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
    except Exception as e:
        st.error(f"❌ Błąd odczytu Excela: {e}")
        return None

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
    
    if 'kolejka' in matches.columns:
        return matches.dropna(subset=['kolejka'])
    return matches

def determine_result_color(row, current_team):
    """Zwraca kolor tekstu na podstawie wyniku meczu."""
    try:
        wynik = str(row['wynik']).strip()
        if '-' not in wynik: return "black"
        
        parts = wynik.split('-')
        score_home = int(parts[0])
        score_away = int(parts[1])
        
        host = str(row['gospodarze']).strip()
        guest = str(row['goście']).strip()
        
        # Logika: Czy wygraliśmy?
        is_win = False
        is_draw = (score_home == score_away)
        is_loss = False
        
        # Sprawdzamy czy wybrany zespół to gospodarz czy gość
        # Używamy in, bo nazwy mogą się różnić (np. "FC Barcelona" vs "Barcelona")
        if current_team in host or host in current_team:
            if score_home > score_away: is_win = True
            elif score_home < score_away: is_loss = True
        elif current_team in guest or guest in current_team:
            if score_away > score_home: is_win = True
            elif score_away < score_home: is_loss = True
            
        if is_win: return "green"
        if is_loss: return "red"
        if is_draw: return "#b58900" # Ciemny żółty/złoty dla lepszej czytelności
        return "black"
        
    except:
        return "black"

def process_team_sheet(df, team_name):
    try:
        match_split = df.index[df.iloc[:, 0].astype(str).str.lower() == 'kolejka'].tolist()
        match_idx = match_split[0] if match_split else len(df)
        
        df_top = df.iloc[:match_idx].copy()
        
        # Szukamy podziału na funkcję (trenerów)
        staff_idx = -1
        for idx, row in df_top.iterrows():
            if row.astype(str).str.contains('funkcja', case=False).any():
                staff_idx = idx
                break
        
        if staff_idx != -1:
            df_players = df_top.loc[:staff_idx-1].copy()
            df_staff_raw = df_top.loc[staff_idx:]
            new_header = df_staff_raw.iloc[0]
            df_staff = df_staff_raw[1:].copy()
            df_staff.columns = [str(c).lower().strip() for c in new_header]
            
            # --- POPRAWKA: USUWANIE PUSTYCH WIERSZY W TRENERACH ---
            if 'funkcja' in df_staff.columns:
                df_staff = df_staff.dropna(subset=['funkcja'])
            # Dodatkowo sprawdzamy imię i nazwisko
            if 'imię i nazwisko' in df_staff.columns:
                df_staff = df_staff.dropna(subset=['imię i nazwisko'])
                
        else:
            df_players = df_top.copy()
            df_staff = pd.DataFrame()

        # --- POPRAWKA: USUWANIE PUSTYCH WIERSZY W ZAWODNIKACH ---
        # Usuwa wiersze podsumowujące (np. tam gdzie są sumy minut, ale brak nazwiska)
        if 'imię i nazwisko' in df_players.columns:
            df_players = df_players.dropna(subset=['imię i nazwisko'])
        else:
            df_players = df_players.dropna(how='all')

        # Piłkarze
        if not df_players.empty:
            df_players.columns = [str(c).lower().strip() for c in df_players.columns]
            df_players.rename(columns={'t': 'numer', 'nr': 'numer'}, inplace=True)
            
            cols_num = ['mecze', 'minuty', 'gole', 'asysty', 'żółte kartki', 'kanadyjka', 'wiek']
            for col in cols_num:
                if col in df_players.columns:
                    df_players[col] = pd.to_numeric(df_players[col], errors='coerce').fillna(0).astype(int)
            
            if 'narodowość' in df_players.columns:
                df_players['flaga_url'] = df_players['narodowość'].apply(get_flag_url)

        # Trenerzy
        if not df_staff.empty:
            if 'narodowość' in df_staff.columns:
                df_staff['flaga_url'] = df_staff['narodowość'].apply(get_flag_url)

        df_matches = clean_matches_table(df, match_idx)
        
        # Formatowanie wyników meczów (Jako tekst, żeby nie było dat)
        if not df_matches.empty and 'wynik' in df_matches.columns:
            df_matches['wynik'] = df_matches['wynik'].astype(str)
        
        return df_players, df_staff, df_matches

    except Exception as e:
        st.warning(f"⚠️ Błąd przetwarzania '{team_name}': {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- APP START ---

data_sheets = load_all_data(EXCEL_FILE)

if data_sheets:
    st.sidebar.title("Menu")
    sheet_names = list(data_sheets.keys())
    special_sheets = ['Tabela', 'Strzelcy', 'Legenda', 'Info']
    team_names = sorted([n for n in sheet_names if n not in special_sheets])
    
    page = st.sidebar.radio("Wybierz widok", ["🏆 Tabela Ligowa", "🎯 Strzelcy", "⚽ Drużyny"])
    
    # --- TABELA LIGOWA ---
    if page == "🏆 Tabela Ligowa":
        st.title("Tabela Ligi Mistrzów 25/26")
        if 'Tabela' in data_sheets:
            df_tabela = data_sheets['Tabela']
            df_tabela = df_tabela.loc[:, ~df_tabela.columns.str.contains('^Unnamed')]
            
            if 'klub' in df_tabela.columns:
                df_tabela['logo_url'] = df_tabela['klub'].apply(get_club_logo_url)
            
            cols = ['Miejsce', 'logo_url', 'klub', 'mecze', 'punkty', 'strzelone', 'stracone', 'bilans', 'wygrane', 'remisy', 'porażki']
            final_cols = [c for c in cols if c in df_tabela.columns]
            
            st.dataframe(
                df_tabela[final_cols],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "logo_url": st.column_config.ImageColumn("Herb", width="small"),
                    "bilans": st.column_config.ProgressColumn("Bilans", min_value=-20, max_value=50, format="%d"),
                    "Miejsce": st.column_config.NumberColumn("#", format="%d")
                }
            )
        else:
            st.info("Brak arkusza Tabela.")

    # --- STRZELCY ---
    elif page == "🎯 Strzelcy":
        st.title("Najlepsi Strzelcy")
        if 'Strzelcy' in data_sheets:
            df_strzelcy = data_sheets['Strzelcy']
            
            if 'kraj' in df_strzelcy.columns:
                df_strzelcy['flaga_url'] = df_strzelcy['kraj'].apply(get_flag_url)
            
            if 'data urodzenia' in df_strzelcy.columns:
                df_strzelcy['data urodzenia'] = pd.to_datetime(df_strzelcy['data urodzenia'], errors='coerce').dt.date

            st.dataframe(
                df_strzelcy,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "data urodzenia": st.column_config.DateColumn("Data urodzenia", format="DD.MM.YYYY"),
                    "flaga_url": st.column_config.ImageColumn("Kraj", width="small")
                }
            )

    # --- DRUŻYNY ---
    elif page == "⚽ Drużyny":
        st.title("Statystyki Drużyn")
        selected_team = st.sidebar.selectbox("Wybierz drużynę", team_names)
        
        if selected_team:
            df_p, df_s, df_m = process_team_sheet(data_sheets[selected_team], selected_team)
            
            st.header(f"Raport: {selected_team}")
            
            if not df_p.empty:
                goals = df_p['gole'].sum() if 'gole' in df_p.columns else 0
                matches = len(df_m)
                st.columns(2)[0].metric("Gole Zespołu", goals)
                st.columns(2)[1].metric("Rozegrane Mecze", matches)
            
            tab1, tab2, tab3 = st.tabs(["Kadra i Sztab", "Terminarz", "Statystyki"])
            
            with tab1:
                # 1. PIŁKARZE
                st.subheader("Zawodnicy")
                if not df_p.empty:
                    cols_p = ['numer', 'flaga_url', 'imię i nazwisko', 'pozycja', 'narodowość', 'wiek', 'mecze', 'gole', 'asysty', 'kanadyjka']
                    final_p = [c for c in cols_p if c in df_p.columns]
                    
                    # Obliczamy lokalne maksimum goli dla paska
                    max_goals = df_p['gole'].max() if 'gole' in df_p.columns and not df_p['gole'].empty else 10
                    
                    st.dataframe(
                        df_p[final_p],
                        use_container_width=True, hide_index=True,
                        column_config={
                            # Usunięto sztywny limit, teraz jest max_goals
                            "gole": st.column_config.ProgressColumn("Gole", format="%d", min_value=0, max_value=int(max_goals)),
                            "flaga_url": st.column_config.ImageColumn("Kraj", width="small"),
                            "numer": st.column_config.NumberColumn("#", format="%d")
                        }
                    )
                else:
                    st.warning("Brak danych zawodników.")
                
                # 2. SZTAB (TRENERZY)
                if not df_s.empty:
                    st.markdown("---")
                    st.subheader("Sztab szkoleniowy")
                    cols_s = ['flaga_url', 'imię i nazwisko', 'funkcja', 'narodowość', 'wiek', 'mecze', 'punkty']
                    final_s = [c for c in cols_s if c in df_s.columns]
                    
                    st.dataframe(
                        df_s[final_s],
                        use_container_width=True, hide_index=True,
                        column_config={
                            "flaga_url": st.column_config.ImageColumn("Kraj", width="small")
                        }
                    )

            with tab2:
                if not df_m.empty:
                    # Kolorowanie wyników
                    # Styler w Streamlit
                    def color_results(val):
                        # Ta funkcja działa na pojedynczą komórkę w Pandas Styler
                        # Ale my potrzebujemy kontekstu wiersza.
                        # Więc zrobimy apply na osi 1
                        return ""

                    # Przygotowanie danych do wyświetlenia z kolorami
                    if 'wynik' in df_m.columns:
                        styled_df = df_m.style.apply(lambda x: [f"color: {determine_result_color(x, selected_team)}" if col == 'wynik' else "" for col in x.index], axis=1)
                        st.dataframe(styled_df, use_container_width=True, hide_index=True)
                    else:
                        st.table(df_m)
                else:
                    st.info("Brak terminarza.")
            
            with tab3:
                if not df_p.empty:
                    st.markdown("### Szczegółowe statystyki")
                    c1, c2 = st.columns(2)
                    
                    # WYKRES 1: MINUTY
                    with c1:
                        if 'minuty' in df_p.columns:
                            top_min = df_p.nlargest(15, 'minuty').sort_values('minuty', ascending=True)
                            fig_min = px.bar(top_min, x='minuty', y='imię i nazwisko', orientation='h', 
                                             title="Najwięcej minut na boisku", text='minuty')
                            fig_min.update_traces(marker_color='#1f77b4')
                            st.plotly_chart(fig_min, use_container_width=True)
                        
                    # WYKRES 2: GOLE
                    with c2:
                        scorers = df_p[df_p['gole'] > 0].sort_values('gole', ascending=True)
                        if not scorers.empty:
                            fig_gol = px.bar(scorers, x='gole', y='imię i nazwisko', orientation='h', 
                                             title="Strzelcy", text='gole')
                            fig_gol.update_traces(marker_color='#d62728')
                            st.plotly_chart(fig_gol, use_container_width=True)
                        else:
                            st.info("Brak bramek.")

                    c3, c4 = st.columns(2)
                    
                    # WYKRES 3: ASYSTY
                    with c3:
                        assisters = df_p[df_p['asysty'] > 0].sort_values('asysty', ascending=True)
                        if not assisters.empty:
                            fig_ast = px.bar(assisters, x='asysty', y='imię i nazwisko', orientation='h',
                                             title="Asystenci", text='asysty')
                            fig_ast.update_traces(marker_color='#2ca02c')
                            st.plotly_chart(fig_ast, use_container_width=True)
                        else:
                            st.info("Brak asyst.")
                            
                    # WYKRES 4: KARTKI
                    with c4:
                        if 'żółte kartki' in df_p.columns:
                            cards = df_p[df_p['żółte kartki'] > 0].sort_values('żółte kartki', ascending=True)
                            if not cards.empty:
                                fig_card = px.bar(cards, x='żółte kartki', y='imię i nazwisko', orientation='h',
                                                  title="Żółte kartki", text='żółte kartki')
                                fig_card.update_traces(marker_color='#ff7f0e')
                                st.plotly_chart(fig_card, use_container_width=True)
