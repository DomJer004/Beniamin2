import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Konfiguracja strony
st.set_page_config(page_title="Liga Mistrzów 25/26", layout="wide", page_icon="⚽")

# Stała nazwa pliku Excel (musi być w tym samym folderze co app.py)
EXCEL_FILE = "Liga Mistrzów 25_26.xlsx"

# --- FUNKCJE ŁADOWANIA DANYCH ---

@st.cache_data
def load_all_data(file_path):
    """
    Wczytuje cały plik Excel do słownika DataFrames.
    Kluczami słownika są nazwy arkuszy (np. 'Barcelona', 'Tabela').
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        # sheet_name=None wczytuje WSZYSTKIE arkusze na raz
        all_sheets = pd.read_excel(file_path, sheet_name=None)
        return all_sheets
    except Exception as e:
        st.error(f"Błąd podczas odczytu pliku Excel: {e}")
        return None

def process_team_sheet(df):
    """
    Dzieli arkusz drużyny na część z zawodnikami i część z meczami.
    Szuka wiersza, w którym pierwsza kolumna to 'kolejka'.
    """
    # Znajdź indeks wiersza, który zaczyna sekcję meczową
    # Szukamy słowa 'kolejka' w pierwszej kolumnie (niezależnie od wielkości liter)
    split_indices = df.index[df.iloc[:, 0].astype(str).str.lower() == 'kolejka'].tolist()
    
    if split_indices:
        idx = split_indices[0]
        
        # --- CZĘŚĆ 1: ZAWODNICY (wszystko nad 'kolejka') ---
        df_players = df.iloc[:idx].copy()
        df_players = df_players.dropna(how='all') # Usuń puste wiersze
        
        # Ustawienie nagłówków jeśli pierwszy wiersz to nagłówki (standardowo pandas już to robi, 
        # ale przy złożonych arkuszach warto uważać. Tutaj zakładamy, że pd.read_excel wziął 1 wiersz jako nagłówek)
        
        # Standaryzacja nazw kolumn (np. Ajax miał 't' zamiast 'numer')
        df_players.columns = [str(c).lower() for c in df_players.columns]
        df_players.rename(columns={'t': 'numer', 'nr': 'numer'}, inplace=True)
        
        # Konwersja liczb (czyszczenie błędów)
        cols_to_numeric = ['mecze', 'minuty', 'gole', 'asysty', 'żółte kartki', 'kanadyjka', 'wiek']
        for col in cols_to_numeric:
            if col in df_players.columns:
                df_players[col] = pd.to_numeric(df_players[col], errors='coerce').fillna(0).astype(int)

        # --- CZĘŚĆ 2: MECZE (wszystko od 'kolejka' w dół) ---
        # Pobierz nowy nagłówek z wiersza podziału
        new_header = df.iloc[idx].values
        df_matches = df.iloc[idx+1:].copy()
        df_matches.columns = new_header
        df_matches = df_matches.dropna(subset=['kolejka']) # Usuń puste
        
    else:
        # Jeśli nie znaleziono podziału, uznajemy całość za zawodników
        df_players = df
        df_matches = pd.DataFrame()

    return df_players, df_matches

# --- GŁÓWNA LOGIKA APLIKACJI ---

st.sidebar.title("Menu")
data_sheets = load_all_data(EXCEL_FILE)

if data_sheets is None:
    st.error(f"Nie znaleziono pliku '{EXCEL_FILE}'. Upewnij się, że wgrałeś go na GitHub do tego samego folderu co app.py.")
    st.stop()

# Identyfikacja arkuszy specjalnych
sheet_names = list(data_sheets.keys())
special_sheets = ['Tabela', 'Strzelcy', 'Legenda', 'Info'] # Arkusze niebędące drużynami
team_names = sorted([name for name in sheet_names if name not in special_sheets])

# Wybór widoku
view_options = ["🏆 Tabela Ligowa", "🎯 Strzelcy", "⚽ Drużyny"]
page = st.sidebar.radio("Wybierz widok", view_options)

# --- WIDOK: TABELA ---
if page == "🏆 Tabela Ligowa":
    st.title("Tabela Ligi Mistrzów 25/26")
    if 'Tabela' in data_sheets:
        df_tabela = data_sheets['Tabela']
        
        # Wyświetlanie tabeli
        st.dataframe(
            df_tabela,
            use_container_width=True,
            hide_index=True,
            column_config={
                "logo": st.column_config.ImageColumn("Herb"), # Jeśli masz linki do obrazków
                "bilans": st.column_config.ProgressColumn("Bilans", min_value=-20, max_value=50, format="%d"),
            }
        )
        
        # Wykres punktów
        if 'punkty' in df_tabela.columns and 'klub' in df_tabela.columns:
            fig = px.bar(df_tabela.sort_values('punkty', ascending=True), 
                         x='punkty', y='klub', orientation='h', text='punkty',
                         title="Punkty", color='punkty', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Brak arkusza 'Tabela' w pliku Excel.")

# --- WIDOK: STRZELCY ---
elif page == "🎯 Strzelcy":
    st.title("Najlepsi Strzelcy")
    if 'Strzelcy' in data_sheets:
        df_strzelcy = data_sheets['Strzelcy']
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.dataframe(df_strzelcy, use_container_width=True, hide_index=True)
        with c2:
            if 'liczba goli' in df_strzelcy.columns:
                top10 = df_strzelcy.head(10).sort_values('liczba goli', ascending=True)
                fig = px.bar(top10, x='liczba goli', y='imię i nazwisko', orientation='h', title="Top 10")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Brak arkusza 'Strzelcy' w pliku Excel.")

# --- WIDOK: DRUŻYNY ---
elif page == "⚽ Drużyny":
    st.title("Statystyki Drużyn")
    
    selected_team = st.sidebar.selectbox("Wybierz drużynę", team_names)
    
    if selected_team:
        # Pobierz surowy arkusz i przetwórz go
        raw_df = data_sheets[selected_team]
        df_players, df_matches = process_team_sheet(raw_df)
        
        st.header(f"Raport: {selected_team}")
        
        # KPI
        goals = df_players['gole'].sum() if 'gole' in df_players.columns else 0
        matches_count = len(df_matches)
        avg_age = df_players['wiek'].mean() if 'wiek' in df_players.columns else 0
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Gole zespołu", goals)
        k2.metric("Rozegrane mecze", matches_count)
        k3.metric("Średnia wieku", f"{avg_age:.1f}")
        
        tab1, tab2, tab3 = st.tabs(["Kadra", "Terminarz", "Wykresy"])
        
        with tab1:
            # Wybór kolumn do wyświetlenia
            cols = ['numer', 'imię i nazwisko', 'pozycja', 'narodowość', 'wiek', 'mecze', 'gole', 'asysty', 'kanadyjka']
            valid_cols = [c for c in cols if c in df_players.columns]
            
            st.dataframe(
                df_players[valid_cols],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "gole": st.column_config.ProgressColumn("Gole", min_value=0, max_value=20, format="%d"),
                }
            )
            
        with tab2:
            if not df_matches.empty:
                st.table(df_matches)
            else:
                st.info("Brak danych o meczach.")
                
        with tab3:
            if not df_players.empty:
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    if 'pozycja' in df_players.columns:
                        st.caption("Podział kadry wg pozycji")
                        fig_pie = px.pie(df_players, names='pozycja', hole=0.4)
                        st.plotly_chart(fig_pie, use_container_width=True)
                
                with col_chart2:
                    if 'wiek' in df_players.columns and 'minuty' in df_players.columns:
                        st.caption("Wiek vs Minuty na boisku")
                        fig_scat = px.scatter(df_players, x='wiek', y='minuty', size='mecze', 
                                              color='pozycja', hover_name='imię i nazwisko')
                        st.plotly_chart(fig_scat, use_container_width=True)