import pandas as pd

def clean_centre_service(df):
    """
    Nettoie et enrichit le DataFrame des centres de services.
    - Conversion de la date d'ouverture
    - Extraction de l'année et du mois (Feature Engineering)
    - Harmonisation textuelle
    """
    # Copie pour éviter de modifier l'original
    df_clean = df.copy()

    # --- 1. Conversion Temporelle ---
    # Conversion de la colonne date_ouverture en format datetime
    df_clean['date_ouverture'] = pd.to_datetime(df_clean['date_ouverture'], errors='coerce')

    # --- 2. Feature Engineering (Extraction) ---
    # Création des colonnes année et mois à partir de la date
    df_clean['annee_ouverture'] = df_clean['date_ouverture'].dt.year
    df_clean['mois_ouverture'] = df_clean['date_ouverture'].dt.month

    # --- 3. Harmonisation des colonnes textuelles (Optionnel mais recommandé) ---
    # Mise en majuscule de la première lettre pour les localisations
    cols_loc = ['region', 'prefecture', 'commune', 'quartier', 'nom_centre']
    for col in cols_loc:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip().str.title()

    # --- 4. Nettoyage des colonnes catégorielles ---
    # S'assurer que les statuts et types sont bien formatés
    for col in ['type_centre', 'statut_centre', 'equipement_numerique']:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip().str.capitalize()

    return df_clean