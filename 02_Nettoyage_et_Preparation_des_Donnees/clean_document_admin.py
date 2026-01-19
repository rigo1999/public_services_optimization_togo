import pandas as pd

def clean_demandes_data(df):
    """
    Transforme les numéros de mois en noms et optimise les types de données.
    """
    # 1. Création du dictionnaire de correspondance
    mois_map = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }
    
    # 2. Copie du dataframe pour ne pas modifier l'original
    df_clean = df.copy()
    
    # 3. CRÉATION de la nouvelle colonne (sans toucher à 'mois')
    df_clean['mois_nom'] = df_clean['mois'].map(mois_map)
    
    # 4. Création de la colonne période
    df_clean['periode'] = df_clean['mois_nom'].astype(str) + " " + df_clean['annee'].astype(str)
    
    # 5. Conversion en 'category' (On ajoute 'mois_nom' à la liste)
    # Note : On garde 'mois' en int64 ou on le met en category selon votre besoin
    cols_cat = ['region', 'prefecture', 'commune', 'type_document', 'mois_nom']
    
    for col in cols_cat:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype('category')
        
    return df_clean