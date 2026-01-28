import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Liga Mistrzów 25/26", layout="wide", page_icon="⚽")

EXCEL_FILE = "Liga Mistrzów 25_26.xlsx"

# --- MAPA KODÓW KRAJÓW (Dla API FlagCDN) ---
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
    "Gwinea": "gn", "Gwinea Równikowa": "gq", "Gwinea Bissau": "gw",
    "Burkina Faso": "bf", "RPA": "za", "Zimbabwe": "zw",
    "Republika Zielonego Przylądka": "cv", "Mozambik": "mz", "Libia": "ly",
    
    # Azja
    "Japonia": "jp", "Korea Południowa": "kr", "Chiny": "cn",
    "Australia": "au", "Iran": "ir", "Izrael": "il", "Syria": "sy"
}

# --- MAPA KLUB -> KRAJ (Do Tabeli Ligowej) ---
CLUB_TO_COUNTRY = {
    "Arsenal": "Anglia", "Aston Villa": "Anglia", "Liverpool": "Anglia", "Manchester City": "Anglia", "Chelsea": "Anglia", "Tottenham Hotspur": "Anglia", "Newcastle United": "Anglia",
    "Real Madryt": "Hiszpania", "Barcelona": "Hiszpania", "Atlético Madryt": "Hiszpania", "Girona": "Hiszpania", "Athletic Bilbao": "Hiszpania", "Villarreal": "Hiszpania",
    "Bayern Monachium": "Niemcy", "Borussia Dortmund": "Niemcy", "Bayer Leverkusen": "Niemcy", "RB Leipzig": "Niemcy", "Stuttgart": "Niemcy", "Eintracht Frankfurt": "Niemcy",
    "Inter Mediolan": "Włochy", "AC Milan": "Włochy", "Juventus": "Włochy", "Atalanta": "Włochy", "Bologna": "Włochy", "Napoli": "Włochy",
    "Paris Saint-Germain": "Francja", "Monaco": "Francja", "Brest": "Francja", "Lille": "Francja", "Olympique Marsylia": "Francja",
    "Sporting CP": "Portugalia", "Benfica": "Portugalia",
    "PSV Eindhoven": "Holandia", "Feyenoord": "Holandia", "Ajax": "Holandia",
    "Club Brugge": "Belgia", "Union Saint-Gilloise": "Belgia",
    "Celtic": "Szkocja",
    "Sturm Graz": "Austria", "RB Salzburg": "Austria",
    "Szachtar Donieck": "Ukraina",
    "Dinamo Zagrzeb": "Chorwacja",
    "Crvena Zvezda": "Serbia",
    "Young Boys": "Szwajcaria",
    "Sparta Praga": "Czechy", "Slavia Praga": "Czechy",
    "Slovan Bratysława": "Słowacja",
    "Galatasaray": "Turcja",
    "Kopenhaga": "Dania",
    "Bodo/Glimt": "Norwegia",
    "Olympiacos": "Grecja",
    "Karabach": "Azerbejdżan",
    "Pafos": "Cypr",
    "Kairat Ałmaty": "Kazachstan"
}

def get_flag_url(nationality_str):
    if not isinstance(nationality_str, str) or not nationality_str.strip():
        return None
    first_country = nationality_str.replace("/", ",").split(",")[0].strip()
    if "Konaga" in first_country or "Konga" in first_country: first_country = "Demokratyczna Republika Konga"
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
    return matches.dropna(subset=['kolejka']) if 'kolejka' in matches.columns else matches

def process_team_sheet(df, team_name):
    try:
        # 1. Znajdź początek meczów
        match_split = df.index[df.iloc[:, 0].astype(str).str.lower() == 'kolejka'].tolist()
        match_idx = match_split[0] if match_split else len(df)
        
        df_top = df.iloc[:match_idx].copy()
        
        # 2. Znajdź podział Piłkarze / Trenerzy (szukamy słowa 'rola')
        staff_idx = -1
        for idx, row in df_top.iterrows():
            if row.astype(str).str.contains('rola', case=False).any():
                staff_idx = idx
                break
        
        # 3. Rozdziel dane
        if staff_idx != -1:
            # Piłkarze są powyżej trenerów
            df_players = df_top.loc[:staff_idx-1].dropna(how='all')
            
            # Trenerzy
            df_staff_raw = df_top.loc[staff_idx:]
            new_header = df_staff_raw.iloc[0]
            df_staff = df_staff_raw[1:].copy()
            df_staff.columns = [str(c).lower().strip() for c in new_header]
            df_staff = df_staff.dropna(subset=['rola'])
        else:
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
            else:
                df_players['flaga_url'] = None

        # 5. Czyszczenie Trenerów
        if not df_staff.empty:
            if 'narodowość' in df_staff.columns:
                df_staff['flaga_url'] = df_staff['narodowość'].apply(get_flag_url)
            else:
                df_staff['flaga_url'] = None

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
    
    # --- TABELA LIGOWA ---
    if page == "🏆 Tabela Ligowa":
        st.title("Tabela Ligi Mistrzów 25/26")
        if 'Tabela' in data_sheets:
            df_tabela = data_sheets['Tabela']
            df_tabela = df_tabela.loc[:, ~df_tabela.columns.str.contains('^Unnamed')]
            
            # Dodajemy flagi klubów
            if 'klub' in df_tabela.columns:
                df_tabela['kraj_klubu'] = df_tabela['klub'].apply(lambda x: CLUB_TO_COUNTRY.get(str(x).strip(), ""))
                df_tabela['flaga_url'] = df_tabela['kraj_klubu'].apply(get_flag_url)
            
            # Ukrywamy kolumnę 'logo' i 'kraj_klubu' (zostawiamy tylko obrazek flagi)
            cols = ['Miejsce', 'flaga_url', 'klub', 'mecze', 'punkty', 'strzelone', 'stracone', 'bilans', 'wygrane', 'remisy', 'porażki']
            final_cols = [c for c in cols if c in df_tabela.columns]
            
            st.dataframe(
                df_tabela[final_cols],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "flaga_url": st.column_config.ImageColumn("", width="small"),
                    "bilans": st.column_config.ProgressColumn("Bilans", min_value=-20, max_value=50, format="%d"),
                    "Miejsce": st.column_config.NumberColumn("#", format="%d")
                }
            )
        else:
            st.info("Brak danych.")

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
            
            # KPI
            if not df_p.empty:
                goals = df_p['gole'].sum() if 'gole' in df_p.columns else 0
                matches = len(df_m)
                st.columns(2)[0].metric("Gole", goals)
                st.columns(2)[1].metric("Mecze", matches)
            
            tab1, tab2, tab3 = st.tabs(["Kadra i Sztab", "Terminarz", "Wykresy"])
            
            with tab1:
                # 1. Tabela Piłkarzy
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
                
                # 2. Tabela Trenerów (jeśli istnieje)
                if not df_s.empty:
                    st.divider()
                    st.subheader("Sztab szkoleniowy")
                    cols_s = ['flaga_url', 'imię i nazwisko', 'rola', 'narodowość', 'wiek', 'mecze', 'punkty']
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
                    st.markdown("### Analiza Statystyczna")
                    c1, c2 = st.columns(2)
                    
                    # Wykres 1: Minuty
                    with c1:
                        top_min = df_p.nlargest(15, 'minuty')
                        fig_min = px.bar(top_min, x='minuty', y='imię i nazwisko', orientation='h', 
                                         title="Najwięcej minut na boisku", color='pozycja')
                        fig_min.update_layout(yaxis={'categoryorder':'total ascending'})
                        st.plotly_chart(fig_min, use_container_width=True)
                        
                    # Wykres 2: Gole
                    with c2:
                        scorers = df_p[df_p['gole'] > 0].sort_values('gole', ascending=True)
                        if not scorers.empty:
                            fig_gol = px.bar(scorers, x='gole', y='imię i nazwisko', orientation='h', 
                                             title="Najlepsi Strzelcy", text='gole', color_discrete_sequence=['#ef553b'])
                            st.plotly_chart(fig_gol, use_container_width=True)
                        else:
                            st.info("Brak bramek w zespole.")

                    c3, c4 = st.columns(2)
                    
                    # Wykres 3: Asysty
                    with c3:
                        assisters = df_p[df_p['asysty'] > 0].sort_values('asysty', ascending=True)
                        if not assisters.empty:
                            fig_ast = px.bar(assisters, x='asysty', y='imię i nazwisko', orientation='h',
                                             title="Najlepsi Asystenci", text='asysty', color_discrete_sequence=['#00cc96'])
                            st.plotly_chart(fig_ast, use_container_width=True)
                        else:
                            st.info("Brak asyst.")
                            
                    # Wykres 4: Kartki (jeśli są dane)
                    with c4:
                        if 'żółte kartki' in df_p.columns:
                            cards = df_p[df_p['żółte kartki'] > 0].sort_values('żółte kartki', ascending=True)
                            if not cards.empty:
                                fig_card = px.bar(cards, x='żółte kartki', y='imię i nazwisko', orientation='h',
                                                  title="Żółte kartki", text='żółte kartki', color_discrete_sequence=['#ffd700'])
                                st.plotly_chart(fig_card, use_container_width=True)
