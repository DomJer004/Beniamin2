import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Liga Mistrzów 25/26", layout="wide", page_icon="⚽")

EXCEL_FILE = "Liga Mistrzów 25_26.xlsx"

# --- 1. MAPA KRAJÓW (Dla API FlagCDN - kody ISO) ---
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

# --- 2. MAPA KLUB -> KRAJ (Kompletna dla Ligi Mistrzów) ---
# Służy do przypisania flagi w Tabeli Ligowej
CLUB_TO_COUNTRY = {
    # Anglia
    "Arsenal": "Anglia", "Aston Villa": "Anglia", "Liverpool": "Anglia", 
    "Manchester City": "Anglia", "Chelsea": "Anglia", "Tottenham Hotspur": "Anglia", 
    "Newcastle United": "Anglia", "Newcastle": "Anglia",
    
    # Hiszpania
    "Real Madryt": "Hiszpania", "Barcelona": "Hiszpania", "Atlético Madryt": "Hiszpania", "Atletico Madryt": "Hiszpania",
    "Girona": "Hiszpania", "Athletic Bilbao": "Hiszpania", "Villarreal": "Hiszpania",
    
    # Niemcy
    "Bayern Monachium": "Niemcy", "Borussia Dortmund": "Niemcy", "Bayer Leverkusen": "Niemcy", 
    "RB Leipzig": "Niemcy", "Stuttgart": "Niemcy", "Eintracht Frankfurt": "Niemcy",
    
    # Włochy
    "Inter Mediolan": "Włochy", "AC Milan": "Włochy", "Juventus": "Włochy", 
    "Atalanta": "Włochy", "Bologna": "Włochy", "Napoli": "Włochy",
    
    # Francja
    "Paris Saint-Germain": "Francja", "PSG": "Francja", "Monaco": "Francja", 
    "Brest": "Francja", "Lille": "Francja", "Olympique Marsylia": "Francja", "Marsylia": "Francja",
    
    # Portugalia
    "Sporting CP": "Portugalia", "Benfica": "Portugalia", "FC Porto": "Portugalia",
    
    # Holandia
    "PSV Eindhoven": "Holandia", "PSV": "Holandia", "Feyenoord": "Holandia", "Ajax": "Holandia",
    
    # Belgia
    "Club Brugge": "Belgia", "Brugge": "Belgia", 
    "Union Saint-Gilloise": "Belgia", "USG": "Belgia",
    
    # Pozostałe
    "Celtic": "Szkocja",
    "Sturm Graz": "Austria", "RB Salzburg": "Austria",
    "Szachtar Donieck": "Ukraina",
    "Dinamo Zagrzeb": "Chorwacja",
    "Crvena Zvezda": "Serbia",
    "Young Boys": "Szwajcaria",
    "Sparta Praga": "Czechy", "Slavia Praga": "Czechy",
    "Slovan Bratysława": "Słowacja",
    "Galatasaray": "Turcja", "Fenerbahce": "Turcja",
    "Kopenhaga": "Dania", "FC Kopenhaga": "Dania",
    "Bodo/Glimt": "Norwegia", "Bodo": "Norwegia",
    "Olympiacos": "Grecja", "PAOK": "Grecja",
    "Karabach": "Azerbejdżan",
    "Pafos": "Cypr",
    "Kairat Ałmaty": "Kazachstan", "Kairat": "Kazachstan"
}

def get_flag_url(nationality_str):
    """Pobiera URL flagi z FlagCDN na podstawie nazwy kraju."""
    if not isinstance(nationality_str, str) or not nationality_str.strip():
        return None
    # Bierzemy pierwszy kraj z listy (dla podwójnych obywatelstw)
    first_country = nationality_str.replace("/", ",").split(",")[0].strip()
    
    # Poprawki nazw z Excela
    if "Konaga" in first_country or "Konga" in first_country: 
        first_country = "Demokratyczna Republika Konga"
    if "Niemcu" in first_country: first_country = "Niemcy"
    
    code = COUNTRY_CODES.get(first_country)
    return f"https://flagcdn.com/w40/{code}.png" if code else None

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
    """Czyści tabelę meczów, usuwa puste kolumny i wiersze."""
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

def process_team_sheet(df, team_name):
    try:
        # 1. Znajdź początek meczów (szukamy 'kolejka')
        match_split = df.index[df.iloc[:, 0].astype(str).str.lower() == 'kolejka'].tolist()
        match_idx = match_split[0] if match_split else len(df)
        
        df_top = df.iloc[:match_idx].copy()
        
        # 2. Znajdź podział Piłkarze / Trenerzy (szukamy słowa 'funkcja')
        staff_idx = -1
        for idx, row in df_top.iterrows():
            # Szukamy słowa 'funkcja' w dowolnej kolumnie wiersza
            if row.astype(str).str.contains('funkcja', case=False).any():
                staff_idx = idx
                break
        
        # 3. Rozdziel dane na Piłkarzy i Sztab
        if staff_idx != -1:
            # Piłkarze są powyżej wiersza z "funkcja"
            df_players = df_top.loc[:staff_idx-1].dropna(how='all')
            
            # Trenerzy zaczynają się od wiersza z "funkcja"
            df_staff_raw = df_top.loc[staff_idx:]
            new_header = df_staff_raw.iloc[0] # To jest wiersz z nagłówkami (lp, imię, funkcja...)
            df_staff = df_staff_raw[1:].copy()
            df_staff.columns = [str(c).lower().strip() for c in new_header]
            
            # Usuwamy puste wiersze w sztabie (tam gdzie nie ma wpisanej funkcji)
            if 'funkcja' in df_staff.columns:
                df_staff = df_staff.dropna(subset=['funkcja'])
        else:
            # Jeśli nie ma "funkcji", wszystko to piłkarze
            df_players = df_top.dropna(how='all')
            df_staff = pd.DataFrame()

        # 4. Czyszczenie Piłkarzy
        if not df_players.empty:
            df_players.columns = [str(c).lower().strip() for c in df_players.columns]
            df_players.rename(columns={'t': 'numer', 'nr': 'numer'}, inplace=True)
            
            cols_num = ['mecze', 'minuty', 'gole', 'asysty', 'żółte kartki', 'kanadyjka', 'wiek']
            for col in cols_num:
                if col in df_players.columns:
                    df_players[col] = pd.to_numeric(df_players[col], errors='coerce').fillna(0).astype(int)
            
            if 'narodowość' in df_players.columns:
                df_players['flaga_url'] = df_players['narodowość'].apply(get_flag_url)

        # 5. Czyszczenie Trenerów
        if not df_staff.empty:
            if 'narodowość' in df_staff.columns:
                df_staff['flaga_url'] = df_staff['narodowość'].apply(get_flag_url)

        # 6. Mecze
        df_matches = clean_matches_table(df, match_idx)
        
        return df_players, df_staff, df_matches

    except Exception as e:
        st.warning(f"⚠️ Błąd przetwarzania '{team_name}': {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- START APLIKACJI ---

data_sheets = load_all_data(EXCEL_FILE)

if data_sheets:
    st.sidebar.title("Menu")
    sheet_names = list(data_sheets.keys())
    special_sheets = ['Tabela', 'Strzelcy', 'Legenda', 'Info']
    team_names = sorted([n for n in sheet_names if n not in special_sheets])
    
    page = st.sidebar.radio("Wybierz widok", ["🏆 Tabela Ligowa", "🎯 Strzelcy", "⚽ Drużyny"])
    
    # --- WIDOK: TABELA LIGOWA ---
    if page == "🏆 Tabela Ligowa":
        st.title("Tabela Ligi Mistrzów 25/26")
        if 'Tabela' in data_sheets:
            df_tabela = data_sheets['Tabela']
            # Usuwamy techniczne kolumny (Unnamed)
            df_tabela = df_tabela.loc[:, ~df_tabela.columns.str.contains('^Unnamed')]
            
            # Dopasowanie flagi na podstawie nazwy klubu
            if 'klub' in df_tabela.columns:
                df_tabela['kraj_klubu'] = df_tabela['klub'].apply(lambda x: CLUB_TO_COUNTRY.get(str(x).strip(), ""))
                df_tabela['logo_url'] = df_tabela['kraj_klubu'].apply(get_flag_url)
            
            # Konfiguracja kolumn
            cols = ['Miejsce', 'logo_url', 'klub', 'mecze', 'punkty', 'strzelone', 'stracone', 'bilans', 'wygrane', 'remisy', 'porażki']
            final_cols = [c for c in cols if c in df_tabela.columns]
            
            st.dataframe(
                df_tabela[final_cols],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "logo_url": st.column_config.ImageColumn("Logo", width="small"), # Ukrywamy tekst, pokazujemy obrazek
                    "bilans": st.column_config.ProgressColumn("Bilans", min_value=-20, max_value=50, format="%d"),
                    "Miejsce": st.column_config.NumberColumn("#", format="%d")
                }
            )
        else:
            st.info("Brak arkusza Tabela.")

    # --- WIDOK: STRZELCY ---
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

    # --- WIDOK: DRUŻYNY ---
    elif page == "⚽ Drużyny":
        st.title("Statystyki Drużyn")
        selected_team = st.sidebar.selectbox("Wybierz drużynę", team_names)
        
        if selected_team:
            df_p, df_s, df_m = process_team_sheet(data_sheets[selected_team], selected_team)
            
            st.header(f"Raport: {selected_team}")
            
            # KPI
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
                    
                    st.dataframe(
                        df_p[final_p],
                        use_container_width=True, hide_index=True,
                        column_config={
                            "gole": st.column_config.ProgressColumn("Gole", format="%d", min_value=0, max_value=25),
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
                    # Wybieramy sensowne kolumny dla trenera
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
                    st.table(df_m)
                else:
                    st.info("Brak terminarza.")
            
            with tab3:
                if not df_p.empty:
                    st.markdown("### Szczegółowe statystyki")
                    
                    c1, c2 = st.columns(2)
                    
                    # WYKRES 1: MINUTY (Statystyczny Bar Chart)
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
