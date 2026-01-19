import pandas as pd
import numpy as np

def clean_logs_activite(df):
    """
    Nettoie le DataFrame des logs d'activité.
    Paramètre : df (pandas DataFrame)
    """
    # On travaille sur une copie pour ne pas modifier l'original par accident
    df_clean = df.copy()

    # --- 1. Règle spécifique pour type_document ---
    # Remplacer les valeurs nulles (NaN) par "Non_Renseigné"
    df_clean['type_document'] = df_clean['type_document'].fillna("Non_Renseigné")
    
    # Remplacer les chaînes vides ou espaces par "Inconnu"
    df_clean['type_document'] = df_clean['type_document'].replace(['', ' ', 'nan'], "Inconnu")

    # --- 2. Conversion des types ---
    # Conversion de la date
    if 'date_operation' in df_clean.columns:
        df_clean['date_operation'] = pd.to_datetime(df_clean['date_operation'], errors='coerce')

    # Conversion numérique (remplace les erreurs par 0)
    cols_num = ['nombre_traite', 'delai_effectif', 'nombre_rejete', 'temps_attente_moyen_minutes']
    for col in cols_num:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)

    # --- 3. Nettoyage textuel ---
    cols_str = ['type_operation', 'raison_rejet', 'incident_technique']
    for col in cols_str:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()

    return df_clean