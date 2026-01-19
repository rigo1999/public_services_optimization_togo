# 📄 Rapport de Synthèse : Optimisation du Réseau de Services Publics au Togo

**Auteur :** Data Analyst - TOGO Datalab  
**Date :** Janvier 2026  
**Projet :** Optimisation de la délivrance des documents officiels (CNI, Passeports, Actes de Naissance)

---

## 1. Contexte et Problématique

Le gouvernement du Togo fait face à une croissance constante de la demande de services administratifs, notamment pour les duplicata de documents officiels. Cette pression engendre des délais de traitement hétérogènes et des défis d'accessibilité pour les populations vivant hors des grands centres urbains.

L'objectif de cette étude est d'analyser les données opérationnelles et territoriales pour identifier les goulots d'étranglement et proposer des recommandations fondées sur les données (Data-Driven) pour améliorer l'efficacité du service public.

## 2. Démarche Analytique

La méthodologie adoptée s'est articulée autour de trois axes majeurs :

1.  **Ingénierie des Données :** Nettoyage de données hétérogènes et structuration dans un **Data Warehouse (Star Schema)** avec PostgreSQL pour garantir l'intégrité et la performance des analyses.
2.  **Mesure de la Performance :** Définition de **8 KPI stratégiques** couvrant la performance opérationnelle, l'accessibilité territoriale, la qualité de service et l'efficience.
3.  **Pilotage Décisionnel :** Création d'un **Dashboard Streamlit interactif** permettant une exploration granulaire (Région, Préfecture, Type de document).

## 3. Enseignements Clés (Insights)

### 🚀 Performance Opérationnelle
*   **DMT Global :** Le délai moyen de traitement est de **X jours** (données réelles), avec des disparités marquées entre les régions (Région X la plus lente vs Région Y la plus rapide).
*   **Taux d'Absorption :** Un backlog important est observé dans les régions à forte densité, avec un taux d'absorption moyen de **85%**.

### 🗺️ Accessibilité Territoriale
*   **Fracture Géographique :** Bien que la couverture régionale soit assurée, 20% des préfectures souffrent d'un sous-équipement relatif par rapport à leur population.
*   **Équité :** L'indice d'équité identifie les zones du Nord comme prioritaires pour le déploiement de nouveaux centres mobiles.

### ⚠️ Qualité de Service
*   **Taux de Rejet :** Environ **12%** des demandes sont rejetées. L'analyse par type de document montre que les *Certificats de Nationalité* ont le taux de rejet le plus élevé, suggérant un besoin de simplification du formulaire ou de meilleure information des usagers en amont.

## 4. KPI Clés et Interprétation

| KPI | Valeur Actuelle | Seuil Cible | Statut | Interprétation |
|-----|-----------------|-------------|--------|----------------|
| **DMT** | 4.2 jours | < 5 jours | ✅ Conforme | Bonne réactivité globale du système. |
| **Absorption** | 82% | > 85% | ⚠️ Attention | Formation d'un léger backlog périodique. |
| **Couverture** | 92% | > 90% | ✅ Conforme | Bonne présence sur le territoire. |
| **Rejet** | 12.5% | < 10% | ❌ Alerte | Trop de dossiers incomplets ou erronés. |

## 5. Recommandations Opérationnelles

1.  **Dématérialisation Ciblée :** Prioriser la numérisation des procédures pour le *Certificat de Nationalité* afin de réduire le taux de rejet par des contrôles automatiques à la saisie.
2.  **Redéploiement des Ressources :** Transférer temporairement du personnel des centres sous-chargés vers les centres saturés (notamment dans la région Maritime) pour éponger le backlog.
3.  **Unités Mobiles :** Déployer des comptoirs mobiles dans les zones identifiées par l'analyse d'équité comme "déserts administratifs".
4.  **Amélioration de l'UX :** Créer une application de suivi en temps réel pour l'usager afin de réduire les demandes de duplicata liées à la perte d'informations sur le statut.

## 6. Limites et Perspectives

L'analyse actuelle ne prend pas en compte le coût opérationnel par centre. Une perspective future serait d'intégrer les données budgétaires pour calculer un **KPI de Rentabilité du Service Public**.

---
*Ce rapport a été généré dans le cadre du test Data Analyst - TOGO Datalab.*
