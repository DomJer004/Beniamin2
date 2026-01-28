import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Konfiguracja strony
st.set_page_config(page_title="Liga Mistrzów 25/26", layout="wide", page_icon="⚽")

# Stała nazwa pliku Excel
EXCEL_FILE = "Liga Mistrzów 25_26.xlsx"

# --- FUNKCJE POMOCNICZE ---

@st.cache_data
def load_all_data(file_path):
    if not os.path.exists(file_path):
        st.error(f"❌ Nie znaleziono pliku: {file_path}")
        return None
    try:
        # engine='openpyxl' jest kluczowy dla plików .xlsx
        all_sheets = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
        return all_sheets
    except Exception as e:
        st.error(f"❌ Błąd odczytu Excela: {e}")
        return None

def clean_matches_table(df, start_row_idx):
    """Czyści tabelę meczów, usuwając puste kolumny."""
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
            
            # Standaryzacja nagłówków (małe litery, bez spacji)
            df_players.columns = [str(c).lower().strip() for c in df_players.columns]
            df_players.rename(columns={'t': 'numer', 'nr': 'numer'}, inplace=True)
            
            # Konwersja liczb
            cols_to_numeric = ['mecze', 'minuty', 'gole', 'asysty', 'żółte kartki', 'kanadyjka', 'wiek']
            for col in cols_to_numeric:
                if col in df_players.columns:
                    df_players[col] = pd.to_numeric(df_players[col], errors='coerce').fillna(0).astype(int)

            # --- ŁĄCZENIE FLAGI Z NARODOWOŚCIĄ ---
            # Sprawdzamy czy mamy obie kolumny: 'flaga' i 'narodowość'
            if 'flaga' in df_players.columns and 'narodowość' in df_players.columns:
                # Tworzymy nową kolumnę 'kraj', która łączy flagę i nazwę
                # Używamy .fillna(''), żeby uniknąć błędów przy pustych polach
                df_players['kraj'] = df_players['flaga'].astype(str).replace('nan', '') + " " + df_players['narodowość'].astype(str).replace('nan', '')
            elif 'narodowość' in df_players.columns:
                 # Jeśli nie ma flag, zostaje sama narodowość
                 df_players['kraj'] = df_players['narodowość']
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
    team_names = sorted([n for n in sheet_names if n not in special_sheets])
    
    page = st.sidebar.radio("Wybierz widok", ["🏆 Tabela Ligowa", "🎯 Strzelcy", "⚽ Drużyny"])
    
    # --- TABELA ---
    if page == "🏆 Tabela Ligowa":
        st.title("Tabela Ligi Mistrzów 25/26")
        if 'Tabela' in data_sheets:
            df_tabela = data_sheets['Tabela']
            df_tabela = df_tabela.loc[:, ~df_tabela.columns.str.contains('^Unnamed')]
            st.dataframe(df_tabela, use_container_width=True, hide_index=True)
        else:
            st.info("Brak arkusza 'Tabela'.")

    # --- STRZELCY ---
    elif page == "🎯 Strzelcy":
        st.title("Najlepsi Strzelcy")
        if 'Strzelcy' in data_sheets:
            df_strzelcy = data_sheets['Strzelcy']
            st.dataframe(df_strzelcy, use_container_width=True, hide_index=True)
        else:
            st.info("Brak arkusza 'Strzelcy'.")

    # --- DRUŻYNY ---
    elif page == "⚽ Drużyny":
        st.title("Statystyki Drużyn")
        selected_team = st.sidebar.selectbox("Wybierz drużynę", team_names)
        
        if selected_team:
            df_p, df_m = process_team_sheet(data_sheets[selected_team], selected_team)
            
            st.header(f"Raport: {selected_team}")
            
            # KPI
            if not df_p.empty:
                goals = df_p['gole'].sum() if 'gole' in df_p.columns else 0
                matches = len(df_m)
                
                c1, c2 = st.columns(2)
                c1.metric("Gole", goals)
                c2.metric("Mecze", matches)
            
            tab1, tab2, tab3 = st.tabs(["Kadra", "Terminarz", "Wykresy"])
            
            with tab1:
                if not df_p.empty:
                    # Kolejność kolumn - używamy nowej kolumny 'kraj' zamiast oddzielnych
                    desired_order = [
                        'numer', 'imię i nazwisko', 'pozycja', 
                        'kraj', # <- Tutaj jest połączona flaga i nazwa
                        'wiek', 'mecze', 'gole', 'asysty', 'kanadyjka'
                    ]
                    
                    valid_cols = [c for c in desired_order if c in df_p.columns]
                    
                    st.dataframe(
                        df_p[valid_cols],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "gole": st.column_config.ProgressColumn("Gole", min_value=0, max_value=20, format="%d"),
                            "kraj": st.column_config.Column("Narodowość", width="medium"), # Ładny nagłówek
                            "numer": st.column_config.NumberColumn("#", format="%d")
                        }
                    )
                else:
                    st.warning("Brak danych zawodników.")
            
            with tab2:
                if not df_m.empty:
                    st.table(df_m)
                else:
                    st.info("Brak terminarza.")
            
            with tab3:
                if not df_p.empty and 'pozycja' in df_p.columns:
                     fig = px.pie(df_p, names='pozycja', title='Pozycje', hole=0.4)
                     st.plotly_chart(fig)