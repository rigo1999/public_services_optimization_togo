# clean_demandes_data.py
import pandas as pd
import numpy as np

def clean_demandes_data(input_path='d:/public_services_optimization_togo/data_raw/demandes_service_public.csv', 
                         output_path = 'd:/public_services_optimization_togo/02_Nettoyage_et_Preparation_des_Donnees/data_cleaned/demande_services_public_cleaned.csv',
                         documentation_path='d:/public_services_optimization_togo/02_Nettoyage_et_Preparation_des_Donnees/data_cleaned/documentation_demandes_cleaning.txt'):
    """
    Nettoie et prépare le jeu de données des demandes de services publics.

    Étapes de nettoyage :
    1. Chargement des données.
    2. Conversion du type de données pour 'date_demande'.
    3. Traitement des doublons sur 'demande_id'.
    4. Traitement des valeurs manquantes :
        - 'motif_demande': Imputation basée sur 'statut_demande'.
        - 'quartier': Imputation par 'Inconnu'.
        - 'age_demandeur': Imputation par la médiane.
        - 'sexe_demandeur': Imputation par le mode.
    5. Correction des incohérences et harmonisation des formats (si nécessaire, ajoutable ici).
    6. Ajout de colonnes de temps (année, mois, jour de la semaine).
    7. Sauvegarde du dataset nettoyé et de la documentation des choix.
    """
    
    # --- 1. Chargement des données ---
    try:
        df = pd.read_csv(input_path)
        print(f"Chargement de {input_path} réussi. Dimensions initiales: {df.shape}")
    except FileNotFoundError:
        print(f"Erreur: Le fichier {input_path} n'a pas été trouvé. Veuillez vérifier le chemin.")
        return None
    except Exception as e:
        print(f"Une erreur est survenue lors du chargement: {e}")
        return None

    documentation = []
    documentation.append("--- Documentation du Nettoyage de 'demande_services_public.csv' ---\n")
    documentation.append(f"Date du nettoyage: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    documentation.append(f"Dimensions initiales du DataFrame: {df.shape}\n")

    # --- 2. Conversion du type de données pour 'date_demande' ---
    initial_type = df['date_demande'].dtype
    df['date_demande'] = pd.to_datetime(df['date_demande'])
    documentation.append(f"Converti 'date_demande' de {initial_type} à datetime.\n")
    print(f"Converti 'date_demande' de {initial_type} à datetime.")

    # --- 3. Traitement des doublons sur 'demande_id' ---
    initial_duplicates = df['demande_id'].duplicated().sum()
    if initial_duplicates > 0:
        df.drop_duplicates(subset=['demande_id'], keep='first', inplace=True)
        documentation.append(f"Supprimé {initial_duplicates} doublons basés sur 'demande_id'. Dimensions après suppression: {df.shape}\n")
        print(f"Supprimé {initial_duplicates} doublons basés sur 'demande_id'. Dimensions après suppression: {df.shape}")
    else:
        documentation.append("Aucun doublon trouvé sur 'demande_id'.\n")
        print("Aucun doublon trouvé sur 'demande_id'.")
        
    # --- 4. Traitement des valeurs manquantes ---
    
    # 4.1. 'motif_demande'
    # Imputation: Si statut_demande est 'Acceptée' ou 'En cours', le motif n'est pas applicable.
    # Sinon, si 'Rejetée', le motif devrait être présent. Pour les manquants sur 'Rejetée', nous pouvons imputer par 'Non Spécifié'.
    missing_motif_before = df['motif_demande'].isnull().sum()
    df.loc[df['statut_demande'].isin(['Acceptée', 'En cours']) & df['motif_demande'].isnull(), 'motif_demande'] = 'Non Applicable'
    df['motif_demande'].fillna('Non Spécifié (Rejet)', inplace=True) # Pour les rejets sans motif
    documentation.append(f"Traitement de 'motif_demande': {missing_motif_before} manquants avant. Imputés par 'Non Applicable' si statut est Acceptée/En cours, ou par 'Non Spécifié (Rejet)' si statut est Rejetée et motif manquant.\n")
    print(f"Traitement de 'motif_demande': {missing_motif_before} manquants avant. Imputés par 'Non Applicable' ou 'Non Spécifié (Rejet)'.")

    # 4.2. 'quartier'
    missing_quartier_before = df['quartier'].isnull().sum()
    df['quartier'].fillna('Inconnu', inplace=True)
    documentation.append(f"Traitement de 'quartier': {missing_quartier_before} manquants avant. Imputés par 'Inconnu'.\n")
    print(f"Traitement de 'quartier': {missing_quartier_before} manquants avant. Imputés par 'Inconnu'.")

    # 4.3. 'age_demandeur'
    missing_age_before = df['age_demandeur'].isnull().sum()
    median_age = df['age_demandeur'].median()
    df['age_demandeur'].fillna(median_age, inplace=True)
    df['age_demandeur'] = df['age_demandeur'].astype(int) # Convertir en entier après imputation
    documentation.append(f"Traitement de 'age_demandeur': {missing_age_before} manquants avant. Imputés par la médiane ({median_age}). Converti en entier.\n")
    print(f"Traitement de 'age_demandeur': {missing_age_before} manquants avant. Imputés par la médiane ({median_age}). Converti en entier.")

    # 4.4. 'sexe_demandeur'
    missing_sexe_before = df['sexe_demandeur'].isnull().sum()
    mode_sexe = df['sexe_demandeur'].mode()[0] # mode() peut retourner plusieurs valeurs, on prend la première
    df['sexe_demandeur'].fillna(mode_sexe, inplace=True)
    documentation.append(f"Traitement de 'sexe_demandeur': {missing_sexe_before} manquants avant. Imputés par le mode ({mode_sexe}).\n")
    print(f"Traitement de 'sexe_demandeur': {missing_sexe_before} manquants avant. Imputés par le mode ({mode_sexe}).")

    # --- 5. Correction des incohérences et harmonisation des formats ---
    # --- 5. Correction des incohérences et harmonisation des formats ---
    def fix_encoding(text):
        if not isinstance(text, str): return text
        # Mapping of mangled characters
        # 0x01F8 is 'Ǹ' which replaces 'é'
        text = text.replace(chr(0x01F8), 'é')
        # Common mangled 'é' in other encodings
        text = text.replace('\ufffd', 'é') 
        return text

    # Harmonisation des statuts (Spec: Validée, Rejetée, En Attente)
    status_mapping = {
        'Traitee': 'Validée',
        'Traitée': 'Validée',
        'Rejetée': 'Rejetée',
        'Rejetée': 'Rejetée',
        'En Cours': 'En Attente',
        'En cours': 'En Attente',
        'Acceptée': 'Validée'
    }

    cols_category = ['region', 'prefecture', 'commune', 'quartier', 'type_document', 
                'categorie_document', 'motif_demande', 'statut_demande', 'canal_demande', 'sexe_demandeur']
    
    for col in cols_category:
        if col in df.columns:
            # 1. Strip and fix mangled chars
            df[col] = df[col].astype(str).str.strip().apply(fix_encoding)
            
            # 2. Normalize spaces
            df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
            
            # 3. Handle special status mapping
            if col == 'statut_demande':
                # Exact match first, then partial if needed
                df[col] = df[col].replace(status_mapping)
                # Ensure no weird characters left
                df[col] = df[col].replace('Rejetée', 'Rejetée').replace('Validée', 'Validée')
            else:
                df[col] = df[col].str.title()

    documentation.append("Harmonisation des statuts et correction des erreurs d'encodage (Ǹ -> é, etc.).\n")
    print("Harmonisation des statuts et correction des erreurs d'encodage.")

    # Assurer que les taux sont bien entre 0 et 1
    df['taux_rejet'] = pd.to_numeric(df['taux_rejet'], errors='coerce').fillna(0).clip(0, 1)
    documentation.append("Clipé 'taux_rejet' pour s'assurer qu'il est entre 0 et 1.\n")

    # --- 6. Ajout de colonnes de temps (Année, Mois, Jour de la semaine) ---
    df['annee_demande'] = df['date_demande'].dt.year
    df['mois_demande'] = df['date_demande'].dt.month
    df['jour_semaine_demande'] = df['date_demande'].dt.day_name()
    documentation.append("Ajout des colonnes 'annee_demande', 'mois_demande', 'jour_semaine_demande' à partir de 'date_demande'.\n")
    print("Ajout des colonnes 'annee_demande', 'mois_demande', 'jour_semaine_demande'.")

    documentation.append(f"\nDimensions finales du DataFrame nettoyé: {df.shape}\n")
    print(f"Dimensions finales du DataFrame nettoyé: {df.shape}")

    # --- 7. Sauvegarde du dataset nettoyé et de la documentation ---
    output_dir = output_path.rsplit('/', 1)[0]
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    df.to_csv(output_path, index=False)
    documentation.append(f"Dataset nettoyé sauvegardé à: {output_path}\n")
    print(f"Dataset nettoyé sauvegardé à: {output_path}")

    with open(documentation_path, 'w', encoding='utf-8') as f:
        f.writelines(documentation)
    print(f"Documentation des choix de nettoyage sauvegardée à: {documentation_path}")

    return df

if __name__ == "__main__":
    print("Démarrage du script de nettoyage pour demande_services_public.csv...")
    cleaned_df = clean_demandes_data()
    if cleaned_df is not None:
        print("\nNettoyage terminé. Aperçu du DataFrame nettoyé:")
        display(cleaned_df.head())
        print("\nInformations finales du DataFrame nettoyé:")
        cleaned_df.info()
        print("\nRésumé des valeurs manquantes dans le DataFrame nettoyé:")
        print(cleaned_df.isnull().sum()[cleaned_df.isnull().sum() > 0]) # Devrait être vide