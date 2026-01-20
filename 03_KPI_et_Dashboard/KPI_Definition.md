# Définition des KPI - Optimisation des Services Publics au Togo

Ce document définit le cadre complet des indicateurs clés de performance (KPI) pour le pilotage du réseau de délivrance de documents officiels au Togo. Les KPI sont structurés en 5 catégories métier avec 8 indicateurs couvrant l'ensemble des axes de performance requis.

---

##  Synthèse des KPI

**Total KPI définis:** 8 indicateurs

| # | KPI | Catégorie | Cible | Source Données |
|---|-----|-----------|-------|-----------------|
| KPI-001 | Délai moyen de traitement | Performance Opérationnelle | < 5 jours | dw.fact_demandes + dw.dim_centre |
| KPI-002 | Taux d'absorption des demandes | Performance Opérationnelle | > 85% | dw.fact_demandes + dw.dim_centre |
| KPI-003 | Taux de couverture territoriale | Accessibilité/Couverture | > 90% | dw.dim_centre + dw.dim_territoire |
| KPI-004 | Ratio équité d'accès par région | Accessibilité/Couverture | ≤ 1.5 | dw.dim_centre + dw.dim_socioeconomique |
| KPI-005 | Taux de rejet des demandes | Qualité de Service | < 10% | dw.fact_demandes |
| KPI-006 | Charge de travail par agent | Efficience/Charge | < 20 demandes/jour | dw.fact_demandes + dw.dim_centre |
| KPI-007 | Performance par type de document | Efficience/Charge | Analyse comparative | dw.fact_demandes + dw.dim_document |
| KPI-008 | Taux de saturation des centres | Efficience/Charge | < 80% | dw.fact_demandes + dw.dim_centre |

---

##  Détail des KPI

### **CATÉGORIE 1: PERFORMANCE OPÉRATIONNELLE**

---

#### **KPI-001: Délai Moyen de Traitement des Demandes**

| Propriété | Valeur |
|-----------|--------|
| **Nom** | Délai Moyen de Traitement (DMT) |
| **Objectif Métier** | Réduire le temps d'attente des usagers et améliorer la réactivité opérationnelle |
| **Description** | Temps moyen écoulé (en jours) entre la soumission d'une demande et sa finalisation (validation ou rejet). Un délai faible indique une excellente efficacité opérationnelle. |
| **Interprétation** | • **< 3 jours:** Excellent (réactivité forte) • **3-5 jours:** Bon (normal) • **5-10 jours:** Acceptable (risque d'insatisfaction) • **> 10 jours:** Critique (amélioration urgente) |
| **Règle de Calcul** | `MOYENNE(date_fin - date_debut) en jours`  où date_fin = date de validation/rejet et date_debut = date de soumission |
| **Granularité** | Par centre, par région, par type de document, global |
| **Fréquence** | Quotidienne (comparaison jour/jour-1), mensuelle, trimestrielle |

**SQL - Requête Complète Commentée:**
```sql
-- KPI-001: Délai Moyen de Traitement (DMT)
-- Calcul du temps moyen entre soumission et finalisation des demandes
-- Basé sur la date de demande et de la dernière mise à jour de statut
SELECT 
    -- Identifiants et informations géographiques
    dt.region,
    dt.prefecture, 
    dc.nom_centre,
    dd.type_document,
    
    -- Calculs temporels
    COUNT(fd.id_demande)::INTEGER as nombre_demandes,
    ROUND(AVG(EXTRACT(DAY FROM (fd.date_statut_update - fd.date_demande)))::NUMERIC, 2) as delai_moyen_jours,
    MIN(EXTRACT(DAY FROM (fd.date_statut_update - fd.date_demande)))::INTEGER as delai_min_jours,
    MAX(EXTRACT(DAY FROM (fd.date_statut_update - fd.date_demande)))::INTEGER as delai_max_jours,
    ROUND(STDDEV(EXTRACT(DAY FROM (fd.date_statut_update - fd.date_demande)))::NUMERIC, 2) as ecart_type_jours,
    
    -- Contexte
    CURRENT_TIMESTAMP as date_extraction
FROM dw.fact_demandes fd
LEFT JOIN dw.dim_centre dc ON fd.id_centre = dc.centre_id
LEFT JOIN dw.dim_territoire dt ON dc.id_territoire = dt.territoire_id
LEFT JOIN dw.dim_document dd ON fd.id_document = dd.document_id
WHERE fd.date_demande IS NOT NULL 
  AND fd.date_statut_update IS NOT NULL
  AND fd.date_statut_update >= fd.date_demande  -- Validation logique
GROUP BY dt.region, dt.prefecture, dc.nom_centre, dd.type_document
ORDER BY delai_moyen_jours DESC;

-- Vue alternative: Global
SELECT 
    ROUND(AVG(EXTRACT(DAY FROM (fd.date_statut_update - fd.date_demande)))::NUMERIC, 2) as delai_moyen_global_jours,
    COUNT(*) as nombre_total_demandes
FROM dw.fact_demandes fd
WHERE fd.date_demande IS NOT NULL AND fd.date_statut_update IS NOT NULL;
```

---

#### **KPI-002: Taux d'Absorption des Demandes**

| Propriété | Valeur |
|-----------|--------|
| **Nom** | Taux d'Absorption des Demandes |
| **Objectif Métier** | Mesurer la capacité opérationnelle des centres à traiter les demandes reçues |
| **Description** | Pourcentage de demandes traitées (validées + rejetées) par rapport au volume total reçu. Un taux élevé (>85%) indique une bonne absorption. |
| **Interprétation** | • **> 90%:** Excellent (forte capacité) • **85-90%:** Bon (normal) • **75-85%:** Acceptable (attention requise) • **< 75%:** Critique (accumulation de backlog) |
| **Règle de Calcul** | `(Demandes Traitées / Demandes Totales) × 100` où Demandes Traitées = status IN (Validée, Rejetée, Finalisée) |
| **Granularité** | Par centre, par région, par période, global |
| **Fréquence** | Quotidienne, hebdomadaire, mensuelle |

**SQL - Requête Complète Commentée:**
```sql
-- KPI-002: Taux d'Absorption des Demandes
-- Pourcentage de demandes traitées vs total reçu
-- Indicateur de la capacité du système à traiter les demandes
SELECT 
    -- Contexte géographique
    dt.region,
    dt.prefecture,
    dc.nom_centre,
    
    -- Comptages
    COUNT(CASE WHEN fd.statut IN ('Validée', 'Rejetée', 'Finalisée') THEN 1 END)::INTEGER as demandes_traitees,
    COUNT(CASE WHEN fd.statut = 'En Attente' THEN 1 END)::INTEGER as demandes_en_attente,
    COUNT(*)::INTEGER as demandes_totales,
    
    -- Calcul du taux (%)
    ROUND(
        (COUNT(CASE WHEN fd.statut IN ('Validée', 'Rejetée', 'Finalisée') THEN 1 END)::NUMERIC 
         / NULLIF(COUNT(*), 0)) * 100, 
        2
    ) as taux_absorption_pct,
    
    -- Statut du KPI
    CASE 
        WHEN (COUNT(CASE WHEN fd.statut IN ('Validée', 'Rejetée', 'Finalisée') THEN 1 END)::NUMERIC 
              / NULLIF(COUNT(*), 0)) * 100 > 90 THEN 'Excellent (>90%)'
        WHEN (COUNT(CASE WHEN fd.statut IN ('Validée', 'Rejetée', 'Finalisée') THEN 1 END)::NUMERIC 
              / NULLIF(COUNT(*), 0)) * 100 > 85 THEN 'Bon (85-90%)'
        WHEN (COUNT(CASE WHEN fd.statut IN ('Validée', 'Rejetée', 'Finalisée') THEN 1 END)::NUMERIC 
              / NULLIF(COUNT(*), 0)) * 100 > 75 THEN 'Acceptable (75-85%)'
        ELSE 'Critique (<75%)'
    END as statut_absorption,
    
    CURRENT_TIMESTAMP as date_extraction
FROM dw.fact_demandes fd
LEFT JOIN dw.dim_centre dc ON fd.id_centre = dc.centre_id
LEFT JOIN dw.dim_territoire dt ON dc.id_territoire = dt.territoire_id
GROUP BY dt.region, dt.prefecture, dc.nom_centre
ORDER BY taux_absorption_pct ASC;

-- Vue alternative: Global
SELECT 
    COUNT(CASE WHEN statut IN ('Validée', 'Rejetée', 'Finalisée') THEN 1 END)::INTEGER as demandes_traitees,
    COUNT(*) as total_demandes,
    ROUND((COUNT(CASE WHEN statut IN ('Validée', 'Rejetée', 'Finalisée') THEN 1 END)::NUMERIC 
           / COUNT(*)) * 100, 2) as taux_absorption_global_pct
FROM dw.fact_demandes;
```

---

### **CATÉGORIE 2: ACCESSIBILITÉ & COUVERTURE TERRITORIALE**

---

#### **KPI-003: Taux de Couverture Territoriale**

| Propriété | Valeur |
|-----------|--------|
| **Nom** | Taux de Couverture Territoriale |
| **Objectif Métier** | Assurer que chaque commune dispose d'un accès à un centre de service public |
| **Description** | Pourcentage de communes/quartiers ayant au moins un centre de service accessible. Objectif: 100% |
| **Interprétation** | • **100%:** Couverture complète • **90-99%:** Très bon (quelques zones non couvertes) • **80-90%:** Bon (régions prioritaires couvertes) • **< 80%:** Critique (zones désservies) |
| **Règle de Calcul** | `(Communes avec Centre / Communes Totales) × 100` |
| **Granularité** | Par région, par préfecture, global |
| **Fréquence** | Mensuelle, trimestrielle |

**SQL - Requête Complète Commentée:**
```sql
-- KPI-003: Taux de Couverture Territoriale
-- Mesure le % de communes ayant accès à au moins un centre
-- Indicateur d'équité d'accès géographique
SELECT 
    dt.region,
    dt.prefecture,
    
    -- Comptage des territoires
    COUNT(DISTINCT dt.territoire_id)::INTEGER as communes_totales,
    COUNT(DISTINCT CASE WHEN dc.centre_id IS NOT NULL THEN dt.territoire_id END)::INTEGER as communes_avec_centre,
    
    -- Calcul du taux de couverture (%)
    ROUND(
        (COUNT(DISTINCT CASE WHEN dc.centre_id IS NOT NULL THEN dt.territoire_id END)::NUMERIC 
         / NULLIF(COUNT(DISTINCT dt.territoire_id), 0)) * 100,
        2
    ) as taux_couverture_pct,
    
    -- Statut du KPI
    CASE 
        WHEN (COUNT(DISTINCT CASE WHEN dc.centre_id IS NOT NULL THEN dt.territoire_id END)::NUMERIC 
              / NULLIF(COUNT(DISTINCT dt.territoire_id), 0)) * 100 = 100 THEN 'Couverture Complète (100%)'
        WHEN (COUNT(DISTINCT CASE WHEN dc.centre_id IS NOT NULL THEN dt.territoire_id END)::NUMERIC 
              / NULLIF(COUNT(DISTINCT dt.territoire_id), 0)) * 100 >= 90 THEN 'Très Bon (90-99%)'
        WHEN (COUNT(DISTINCT CASE WHEN dc.centre_id IS NOT NULL THEN dt.territoire_id END)::NUMERIC 
              / NULLIF(COUNT(DISTINCT dt.territoire_id), 0)) * 100 >= 80 THEN 'Bon (80-89%)'
        ELSE 'Critique (<80%)'
    END as statut_couverture,
    
    CURRENT_TIMESTAMP as date_extraction
FROM dw.dim_territoire dt
LEFT JOIN dw.dim_centre dc ON dt.territoire_id = dc.id_territoire
GROUP BY dt.region, dt.prefecture
ORDER BY taux_couverture_pct DESC;
```

---

#### **KPI-004: Ratio Équité d'Accès par Région**

| Propriété | Valeur |
|-----------|--------|
| **Nom** | Ratio Équité d'Accès par Région |
| **Objectif Métier** | Mesurer l'équité d'accès aux services entre les régions (équilibre population/centre) |
| **Description** | Ratio habitant/centre par région. Un ratio proche de 1 indique une équité maximale; >1.5 indique une inégalité. |
| **Interprétation** | • **≤ 1.0:** Très bon (forte accessibilité) • **1.0-1.5:** Bon (acceptable) • **1.5-2.0:** Moyen (risque d'inégalité) • **> 2.0:** Critique (inégalité forte) |
| **Règle de Calcul** | `MAX(Population Region / Centres Region) / MIN(Population Region / Centres Region)` |
| **Granularité** | Comparaison inter-régionales, global |
| **Fréquence** | Trimestrielle, annuelle |

**SQL - Requête Complète Commentée:**
```sql
-- KPI-004: Ratio Équité d'Accès par Région
-- Mesure l'inégalité d'accès entre régions (ratio pop/centre)
-- Indice d'équité: proche de 1 = équité, >1.5 = inégalité
WITH region_stats AS (
    SELECT 
        dt.region,
        COUNT(DISTINCT dc.centre_id)::INTEGER as nombre_centres,
        SUM(COALESCE(ds.population_totale, 0))::BIGINT as population_totale,
        CASE 
            WHEN COUNT(DISTINCT dc.centre_id) > 0 
            THEN ROUND(SUM(COALESCE(ds.population_totale, 0))::NUMERIC / COUNT(DISTINCT dc.centre_id), 2)
            ELSE 0
        END as population_par_centre
    FROM dw.dim_territoire dt
    LEFT JOIN dw.dim_centre dc ON dt.territoire_id = dc.id_territoire
    LEFT JOIN dw.dim_socioeconomique ds ON dt.territoire_id = ds.id_territoire
    GROUP BY dt.region
)
SELECT 
    region,
    nombre_centres,
    population_totale,
    population_par_centre,
    ROUND((
        MAX(population_par_centre) OVER () / 
        NULLIF(MIN(CASE WHEN population_par_centre > 0 THEN population_par_centre END) OVER (), 0)
    )::NUMERIC, 2) as ratio_equite_global,
    
    CASE 
        WHEN (MAX(population_par_centre) OVER () / 
              NULLIF(MIN(CASE WHEN population_par_centre > 0 THEN population_par_centre END) OVER (), 0)) <= 1.2 
        THEN 'Très Bon (Équité forte)'
        WHEN (MAX(population_par_centre) OVER () / 
              NULLIF(MIN(CASE WHEN population_par_centre > 0 THEN population_par_centre END) OVER (), 0)) <= 1.5 
        THEN 'Bon (Acceptable)'
        WHEN (MAX(population_par_centre) OVER () / 
              NULLIF(MIN(CASE WHEN population_par_centre > 0 THEN population_par_centre END) OVER (), 0)) <= 2.0 
        THEN 'Moyen (Attention)'
        ELSE 'Critique (Inégalité)'
    END as statut_equite,
    
    CURRENT_TIMESTAMP as date_extraction
FROM region_stats
ORDER BY population_par_centre DESC;
```

---

### **CATÉGORIE 3: QUALITÉ DE SERVICE**

---

#### **KPI-005: Taux de Rejet des Demandes**

| Propriété | Valeur |
|-----------|--------|
| **Nom** | Taux de Rejet des Demandes |
| **Objectif Métier** | Identifier et réduire les problèmes de qualité dossier et les insuffisances informationnelles |
| **Description** | Pourcentage de demandes rejetées par rapport au total traité. Un taux élevé (>10%) peut indiquer: dossiers incomplets, manque d'information usager, critères non respectés. |
| **Interprétation** | • **< 5%:** Excellent (très bonne qualité dossier) • **5-10%:** Bon (acceptable) • **10-15%:** Moyen (amélioration recommandée) • **> 15%:** Critique (problème systémique) |
| **Règle de Calcul** | `(Demandes Rejetées / Demandes Traitées) × 100` où Demandes Traitées = Validées + Rejetées |
| **Granularité** | Par centre, par région, par type de document, global |
| **Fréquence** | Quotidienne, hebdomadaire, mensuelle |

**SQL - Requête Complète Commentée:**
```sql
-- KPI-005: Taux de Rejet des Demandes
-- Mesure le % de demandes rejetées pour identifier les problèmes de qualité
-- Rejet = dossier incomplet, info manquante, critères non respectés
SELECT 
    dt.region,
    dt.prefecture,
    dc.nom_centre,
    dd.type_document,
    
    -- Comptages par statut
    COUNT(CASE WHEN fd.statut = 'Rejetée' THEN 1 END)::INTEGER as demandes_rejetees,
    COUNT(CASE WHEN fd.statut = 'Validée' THEN 1 END)::INTEGER as demandes_validees,
    (COUNT(CASE WHEN fd.statut = 'Rejetée' THEN 1 END) + 
     COUNT(CASE WHEN fd.statut = 'Validée' THEN 1 END))::INTEGER as demandes_traitees,
    
    -- Calcul du taux de rejet (%)
    ROUND(
        (COUNT(CASE WHEN fd.statut = 'Rejetée' THEN 1 END)::NUMERIC 
         / NULLIF(COUNT(CASE WHEN fd.statut = 'Rejetée' THEN 1 END) + 
                   COUNT(CASE WHEN fd.statut = 'Validée' THEN 1 END), 0)) * 100,
        2
    ) as taux_rejet_pct,
    
    -- Statut du KPI
    CASE 
        WHEN (COUNT(CASE WHEN fd.statut = 'Rejetée' THEN 1 END)::NUMERIC 
              / NULLIF(COUNT(CASE WHEN fd.statut = 'Rejetée' THEN 1 END) + 
                       COUNT(CASE WHEN fd.statut = 'Validée' THEN 1 END), 0)) * 100 < 5 
        THEN 'Excellent (<5%)'
        WHEN (COUNT(CASE WHEN fd.statut = 'Rejetée' THEN 1 END)::NUMERIC 
              / NULLIF(COUNT(CASE WHEN fd.statut = 'Rejetée' THEN 1 END) + 
                       COUNT(CASE WHEN fd.statut = 'Validée' THEN 1 END), 0)) * 100 < 10 
        THEN 'Bon (5-10%)'
        WHEN (COUNT(CASE WHEN fd.statut = 'Rejetée' THEN 1 END)::NUMERIC 
              / NULLIF(COUNT(CASE WHEN fd.statut = 'Rejetée' THEN 1 END) + 
                       COUNT(CASE WHEN fd.statut = 'Validée' THEN 1 END), 0)) * 100 < 15 
        THEN 'Moyen (10-15%)'
        ELSE 'Critique (>15%)'
    END as statut_qualite,
    
    CURRENT_TIMESTAMP as date_extraction
FROM dw.fact_demandes fd
LEFT JOIN dw.dim_centre dc ON fd.id_centre = dc.centre_id
LEFT JOIN dw.dim_territoire dt ON dc.id_territoire = dt.territoire_id
LEFT JOIN dw.dim_document dd ON fd.id_document = dd.document_id
WHERE fd.statut IN ('Rejetée', 'Validée')
GROUP BY dt.region, dt.prefecture, dc.nom_centre, dd.type_document
ORDER BY taux_rejet_pct DESC;

-- Vue alternative: Global
SELECT 
    COUNT(CASE WHEN statut = 'Rejetée' THEN 1 END)::INTEGER as demandes_rejetees,
    COUNT(CASE WHEN statut = 'Validée' THEN 1 END)::INTEGER as demandes_validees,
    ROUND((COUNT(CASE WHEN statut = 'Rejetée' THEN 1 END)::NUMERIC 
           / NULLIF(COUNT(CASE WHEN statut IN ('Rejetée', 'Validée') THEN 1 END), 0)) * 100, 2) 
           as taux_rejet_global_pct
FROM dw.fact_demandes;
```

---

### **CATÉGORIE 4: EFFICIENCE & CHARGE**

---

#### **KPI-006: Charge de Travail par Agent**

| Propriété | Valeur |
|-----------|--------|
| **Nom** | Charge de Travail par Agent |
| **Objectif Métier** | Optimiser l'allocation des ressources humaines et prévenir la surcharge |
| **Description** | Nombre moyen de demandes traitées par agent par jour. Cible: <20 demandes/jour/agent pour maintenir qualité. |
| **Interprétation** | • **< 15 demandes/jour:** Sous-utilisé (ressources excédentaires) • **15-20 demandes/jour:** Optimal • **20-25 demandes/jour:** Tendu (risque qualité) • **> 25 demandes/jour:** Critique (surcharge) |
| **Règle de Calcul** | `(Total Demandes Traitées / Nombre Agents / Jours Travail) par centre` |
| **Granularité** | Par centre, par région, par type de centre, global |
| **Fréquence** | Hebdomadaire, mensuelle |

**SQL - Requête Complète Commentée:**
```sql
-- KPI-006: Charge de Travail par Agent
-- Mesure le nombre moyen de demandes/agent/jour
-- Cible: <20 demandes/jour pour maintenir la qualité
SELECT 
    dt.region,
    dt.prefecture,
    dc.nom_centre,
    dc.type_centre,
    
    -- Ressources
    dc.personnel_capacite_jour::INTEGER as nombre_agents,
    
    -- Demandes
    COUNT(fd.id_demande)::INTEGER as total_demandes,
    COUNT(DISTINCT DATE(fd.date_demande))::INTEGER as jours_avec_activite,
    
    -- Calcul de la charge (demandes/agent/jour)
    CASE 
        WHEN dc.personnel_capacite_jour > 0 AND COUNT(DISTINCT DATE(fd.date_demande)) > 0
        THEN ROUND(COUNT(fd.id_demande)::NUMERIC / dc.personnel_capacite_jour / 
                   NULLIF(COUNT(DISTINCT DATE(fd.date_demande)), 0), 2)
        ELSE 0
    END as charge_moyen_par_agent_par_jour,
    
    -- Statut du KPI
    CASE 
        WHEN dc.personnel_capacite_jour = 0 THEN 'Données incomplètes'
        WHEN (COUNT(fd.id_demande)::NUMERIC / dc.personnel_capacite_jour / 
              NULLIF(COUNT(DISTINCT DATE(fd.date_demande)), 0)) < 15 
        THEN 'Sous-Utilisé (<15)'
        WHEN (COUNT(fd.id_demande)::NUMERIC / dc.personnel_capacite_jour / 
              NULLIF(COUNT(DISTINCT DATE(fd.date_demande)), 0)) < 20 
        THEN 'Optimal (15-20)'
        WHEN (COUNT(fd.id_demande)::NUMERIC / dc.personnel_capacite_jour / 
              NULLIF(COUNT(DISTINCT DATE(fd.date_demande)), 0)) < 25 
        THEN 'Tendu (20-25)'
        ELSE 'Critique (>25)'
    END as statut_charge,
    
    CURRENT_TIMESTAMP as date_extraction
FROM dw.fact_demandes fd
LEFT JOIN dw.dim_centre dc ON fd.id_centre = dc.centre_id
LEFT JOIN dw.dim_territoire dt ON dc.id_territoire = dt.territoire_id
GROUP BY dt.region, dt.prefecture, dc.nom_centre, dc.type_centre, dc.personnel_capacite_jour, dc.centre_id
ORDER BY charge_moyen_par_agent_par_jour DESC;
```

---

#### **KPI-007: Performance par Type de Document**

| Propriété | Valeur |
|-----------|--------|
| **Nom** | Performance par Type de Document |
| **Objectif Métier** | Identifier les types de documents problématiques et optimiser les processus spécifiques |
| **Description** | Délai moyen et taux de rejet par type de document (CNI, Passeport, etc.). Permet d'identifier les goulets d'étranglement. |
| **Interprétation** | Comparer la performance inter-types; identifier les types avec délais élevés ou taux rejet élevés pour amélioration ciblée. |
| **Règle de Calcul** | `MOYENNE(délai par type)` et `TAUX_REJET(par type)` |
| **Granularité** | Par type de document, par région, global |
| **Fréquence** | Mensuelle, trimestrielle |

**SQL - Requête Complète Commentée:**
```sql
-- KPI-007: Performance par Type de Document
-- Analyse comparative des délais et taux de rejet par type de document
-- Identifie les types problématiques pour amélioration ciblée
SELECT 
    dd.type_document,
    
    -- Volume de demandes
    COUNT(*)::INTEGER as nombre_demandes,
    
    -- Analyse temporelle
    ROUND(AVG(EXTRACT(DAY FROM (fd.date_statut_update - fd.date_demande)))::NUMERIC, 2) as delai_moyen_jours,
    MIN(EXTRACT(DAY FROM (fd.date_statut_update - fd.date_demande)))::INTEGER as delai_min_jours,
    MAX(EXTRACT(DAY FROM (fd.date_statut_update - fd.date_demande)))::INTEGER as delai_max_jours,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(DAY FROM (fd.date_statut_update - fd.date_demande)))::INTEGER as delai_median_jours,
    
    -- Analyse qualité
    COUNT(CASE WHEN fd.statut = 'Validée' THEN 1 END)::INTEGER as demandes_validees,
    COUNT(CASE WHEN fd.statut = 'Rejetée' THEN 1 END)::INTEGER as demandes_rejetees,
    ROUND(
        (COUNT(CASE WHEN fd.statut = 'Rejetée' THEN 1 END)::NUMERIC 
         / NULLIF(COUNT(CASE WHEN fd.statut IN ('Rejetée', 'Validée') THEN 1 END), 0)) * 100,
        2
    ) as taux_rejet_pct,
    
    -- Statut global
    CASE 
        WHEN ROUND(AVG(EXTRACT(DAY FROM (fd.date_statut_update - fd.date_demande)))::NUMERIC, 2) < 5 
             AND (COUNT(CASE WHEN fd.statut = 'Rejetée' THEN 1 END)::NUMERIC 
                  / NULLIF(COUNT(CASE WHEN fd.statut IN ('Rejetée', 'Validée') THEN 1 END), 0)) * 100 < 8
        THEN 'Excellent'
        WHEN ROUND(AVG(EXTRACT(DAY FROM (fd.date_statut_update - fd.date_demande)))::NUMERIC, 2) < 8 
             AND (COUNT(CASE WHEN fd.statut = 'Rejetée' THEN 1 END)::NUMERIC 
                  / NULLIF(COUNT(CASE WHEN fd.statut IN ('Rejetée', 'Validée') THEN 1 END), 0)) * 100 < 12
        THEN 'Bon'
        ELSE 'À Améliorer'
    END as statut_global,
    
    CURRENT_TIMESTAMP as date_extraction
FROM dw.fact_demandes fd
LEFT JOIN dw.dim_document dd ON fd.id_document = dd.document_id
WHERE fd.date_demande IS NOT NULL AND fd.date_statut_update IS NOT NULL
GROUP BY dd.type_document
ORDER BY delai_moyen_jours DESC;
```

---

#### **KPI-008: Taux de Saturation des Centres**

| Propriété | Valeur |
|-----------|--------|
| **Nom** | Taux de Saturation des Centres |
| **Objectif Métier** | Prévenir la surcharge opérationnelle et identifier les besoins de redéploiement |
| **Description** | Ratio entre le volume de demandes en attente et la capacité théorique du centre. Taux >80% indique saturation. |
| **Interprétation** | • **< 50%:** Capacité disponible • **50-80%:** Saturation modérée • **80-100%:** Saturation critique • **> 100%:** Surcharge (backlog) |
| **Règle de Calcul** | `(Demandes En Attente / Capacité Journalière) × 100` |
| **Granularité** | Par centre, par région, global |
| **Fréquence** | Quotidienne, hebdomadaire |

**SQL - Requête Complète Commentée:**
```sql
-- KPI-008: Taux de Saturation des Centres
-- Mesure le ratio demandes_en_attente / capacité
-- Identifie les centres saturés nécessitant intervention
SELECT 
    dt.region,
    dt.prefecture,
    dc.nom_centre,
    dc.type_centre,
    
    -- Capacité théorique
    dc.personnel_capacite_jour::INTEGER as capacite_agents,
    (dc.personnel_capacite_jour * 
     COALESCE(EXTRACT(HOUR FROM dc.heures_ouverture)::INTEGER, 8))::INTEGER as capacite_journaliere_estimee,
    
    -- État des demandes
    COUNT(CASE WHEN fd.statut = 'En Attente' THEN 1 END)::INTEGER as demandes_en_attente,
    COUNT(CASE WHEN fd.statut IN ('Validée', 'Rejetée', 'Finalisée') THEN 1 END)::INTEGER as demandes_traitees,
    COUNT(*)::INTEGER as total_demandes,
    
    -- Calcul du taux de saturation (%)
    ROUND(
        (COUNT(CASE WHEN fd.statut = 'En Attente' THEN 1 END)::NUMERIC 
         / NULLIF((dc.personnel_capacite_jour * 
                   COALESCE(EXTRACT(HOUR FROM dc.heures_ouverture)::INTEGER, 8)), 0)) * 100,
        2
    ) as taux_saturation_pct,
    
    -- Statut du KPI
    CASE 
        WHEN (COUNT(CASE WHEN fd.statut = 'En Attente' THEN 1 END)::NUMERIC 
              / NULLIF((dc.personnel_capacite_jour * 
                       COALESCE(EXTRACT(HOUR FROM dc.heures_ouverture)::INTEGER, 8)), 0)) * 100 < 50 
        THEN 'Capacité Disponible'
        WHEN (COUNT(CASE WHEN fd.statut = 'En Attente' THEN 1 END)::NUMERIC 
              / NULLIF((dc.personnel_capacite_jour * 
                       COALESCE(EXTRACT(HOUR FROM dc.heures_ouverture)::INTEGER, 8)), 0)) * 100 < 80 
        THEN 'Saturation Modérée'
        WHEN (COUNT(CASE WHEN fd.statut = 'En Attente' THEN 1 END)::NUMERIC 
              / NULLIF((dc.personnel_capacite_jour * 
                       COALESCE(EXTRACT(HOUR FROM dc.heures_ouverture)::INTEGER, 8)), 0)) * 100 < 100 
        THEN 'Saturation Critique'
        ELSE 'Surcharge (Backlog)'
    END as statut_saturation,
    
    CURRENT_TIMESTAMP as date_extraction
FROM dw.fact_demandes fd
LEFT JOIN dw.dim_centre dc ON fd.id_centre = dc.centre_id
LEFT JOIN dw.dim_territoire dt ON dc.id_territoire = dt.territoire_id
GROUP BY dt.region, dt.prefecture, dc.nom_centre, dc.type_centre, dc.personnel_capacite_jour, 
         dc.heures_ouverture, dc.centre_id
ORDER BY taux_saturation_pct DESC;
```

---

##  Résumé et Recommandations

### Tableau Synthétique: Cibles et Seuils

| KPI | Excellent | Bon | Acceptable | Critique |
|-----|-----------|-----|-----------|----------|
| KPI-001: DMT | < 3 j | 3-5 j | 5-10 j | > 10 j |
| KPI-002: Absorption | > 90% | 85-90% | 75-85% | < 75% |
| KPI-003: Couverture | 100% | 90-99% | 80-89% | < 80% |
| KPI-004: Équité | ≤ 1.2 | 1.2-1.5 | 1.5-2.0 | > 2.0 |
| KPI-005: Rejet | < 5% | 5-10% | 10-15% | > 15% |
| KPI-006: Charge/Agent | < 15 | 15-20 | 20-25 | > 25 |
| KPI-007: Doc-Type | Délai<5j + Rejet<8% | Délai<8j + Rejet<12% | À Améliorer | À Analyser |
| KPI-008: Saturation | < 50% | 50-80% | 80-100% | > 100% |

### Fréquences de Suivi Recommandées

- **Quotidienne:** KPI-001, KPI-002, KPI-005, KPI-008 (opérationnel)
- **Hebdomadaire:** KPI-006, KPI-007 (ressources et types)
- **Mensuelle:** Tous les KPI (synthèse)
- **Trimestrielle:** KPI-003, KPI-004 (couverture, équité - faible variabilité)

---

##  Prochaines Étapes

1. **Validation des Données:** Exécuter les 8 requêtes SQL sur la base de données PostgreSQL pour valider la cohérence des données
2. **Implémentation Dashboard:** Créer visualisations interactives (Streamlit, Superset ou Power BI) avec filtres dynamiques
3. **Alertes et Monitoring:** Configurer seuils d'alerte automatiques pour chaque KPI
4. **Rapportage Périodique:** Générer rapports KPI mensuels pour la gouvernance
5. **Itération:** Affiner les seuils en fonction du contexte opérationnel réel
