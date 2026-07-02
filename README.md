# AgriStat-BF API

Documentation de l'API pour la plateforme AgriStat-BF.
Le serveur s'exécute localement sur : `http://127.0.0.1:8000`

> 💡 **Astuce** : La façon la plus simple de tester tous ces endpoints sans Postman est d'ouvrir **http://127.0.0.1:8000/docs** dans votre navigateur. C'est une interface interactive (Swagger) qui permet de générer des requêtes en un clic.

### 🛠️ Guide d'utilisation de Swagger (pour les devs Frontend)
L'interface Swagger à l'URL `/docs` est votre meilleur outil pour comprendre l'API :
1. **Explorez les routes** : Les endpoints sont regroupés par entité (Régions, Provinces, etc.). Cliquez sur une route (ex: `GET /api/gestion/regions`) pour l'ouvrir.
2. **"Try it out" (Essayer)** : En haut à droite du panneau ouvert, cliquez sur le bouton blanc **"Try it out"**. Cela débloque les champs pour que vous puissiez envoyer des données.
3. **"Execute" (Exécuter)** : Remplissez les données si nécessaire, puis cliquez sur le gros bouton bleu **"Execute"** apparu plus bas.
4. **Récupérez le code d'intégration** : Swagger affichera l'URL exacte appelée, la commande `curl` correspondante, ainsi que la réponse du serveur (JSON et code HTTP). Vous pouvez vous en inspirer pour vos requêtes `fetch()` ou `axios` !

---

## 1. Endpoints de Gestion (CRUD)

### Régions
- **Lister toutes les régions**
  - **Méthode** : `GET`
  - **URL** : `/api/gestion/regions`
- **Ajouter une région**
  - **Méthode** : `POST`
  - **URL** : `/api/gestion/regions`
  - **Body (JSON)** :
    ```json
    {
      "nom_region": "Cascades",
      "population_totale": 800000,
      "superficie": 18406.0
    }
    ```
- **Remplacer intégralement une région**
  - **Méthode** : `PUT`
  - **URL** : `/api/gestion/regions/{id}`
  - **Body (JSON)** : Doit contenir *tous* les champs.
- **Modifier partiellement une région**
  - **Méthode** : `PATCH`
  - **URL** : `/api/gestion/regions/{id}`
  - **Body (JSON)** : Exemple de modification partielle :
    ```json
    {
      "population_totale": 850000
    }
    ```
- **Supprimer une région**
  - **Méthode** : `DELETE`
  - **URL** : `/api/gestion/regions/{id}`

### Provinces
- **Lister toutes les provinces**
  - **Méthode** : `GET`
  - **URL** : `/api/gestion/provinces`
- **Ajouter une province**
  - **Méthode** : `POST`
  - **URL** : `/api/gestion/provinces`
  - **Body (JSON)** :
    ```json
    {
      "nom_province": "Comoé",
      "id_region": 7,
      "chef_lieu": "Banfora",
      "historique_sinistres": "Inondation 2021"
    }
    ```
- **Remplacer intégralement une province**
  - **Méthode** : `PUT`
  - **URL** : `/api/gestion/provinces/{id}`
- **Modifier partiellement une province**
  - **Méthode** : `PATCH`
  - **URL** : `/api/gestion/provinces/{id}`
- **Supprimer une province**
  - **Méthode** : `DELETE`
  - **URL** : `/api/gestion/provinces/{id}`

### Céréales
- **Lister toutes les céréales**
  - **Méthode** : `GET`
  - **URL** : `/api/gestion/cereales`
- **Ajouter une céréale**
  - **Méthode** : `POST`
  - **URL** : `/api/gestion/cereales`
  - **Body (JSON)** :
    ```json
    {
      "nom_cereale": "Fonio",
      "cycle_maturation": "Court",
      "besoin_hydrique": "Faible"
    }
    ```
- **Remplacer intégralement une céréale**
  - **Méthode** : `PUT`
  - **URL** : `/api/gestion/cereales/{id}`
- **Modifier partiellement une céréale**
  - **Méthode** : `PATCH`
  - **URL** : `/api/gestion/cereales/{id}`
- **Supprimer une céréale**
  - **Méthode** : `DELETE`
  - **URL** : `/api/gestion/cereales/{id}`

### Campagnes Agricoles
- **Lister toutes les campagnes**
  - **Méthode** : `GET`
  - **URL** : `/api/gestion/campagnes`
- **Ajouter une campagne**
  - **Méthode** : `POST`
  - **URL** : `/api/gestion/campagnes`
  - **Body (JSON)** :
    ```json
    {
      "annee": 2026,
      "climat_general": "Prévisions favorables"
    }
    ```
- **Remplacer intégralement une campagne**
  - **Méthode** : `PUT`
  - **URL** : `/api/gestion/campagnes/{id}`
- **Modifier partiellement une campagne**
  - **Méthode** : `PATCH`
  - **URL** : `/api/gestion/campagnes/{id}`
- **Supprimer une campagne**
  - **Méthode** : `DELETE`
  - **URL** : `/api/gestion/campagnes/{id}`

### Productions
- **Lister toutes les productions**
  - **Méthode** : `GET`
  - **URL** : `/api/gestion/productions`
- **Ajouter une production**
  - **Méthode** : `POST`
  - **URL** : `/api/gestion/productions`
  - **Body (JSON)** :
    ```json
    {
      "id_campagne": 3,
      "id_province": 1,
      "id_cereale": 1,
      "superficie_emblavee": 15000.5,
      "quantite_recoltee": 28000.0
    }
    ```
- **Remplacer intégralement une production**
  - **Méthode** : `PUT`
  - **URL** : `/api/gestion/productions/{id}`
- **Modifier partiellement une production**
  - **Méthode** : `PATCH`
  - **URL** : `/api/gestion/productions/{id}`
- **Supprimer une production**
  - **Méthode** : `DELETE`
  - **URL** : `/api/gestion/productions/{id}`

---

## 2. Endpoints d'Analyse et Tableau de Bord

Ces endpoints sont principalement utilisés pour alimenter les graphiques et les statistiques. Ils acceptent souvent un paramètre optionnel `campagne_id` (par défaut 3).

- **KPIs globaux (Production, Superficie, Rendement)**
  - **Méthode** : `GET`
  - **URL** : `/api/dashboard/kpi?campagne_id=3`

- **Production par région (pour graphiques)**
  - **Méthode** : `GET`
  - **URL** : `/api/dashboard/production-par-region?campagne_id=3`

- **Répartition par céréale (pour graphiques)**
  - **Méthode** : `GET`
  - **URL** : `/api/dashboard/repartition-cereales?campagne_id=3`

- **Alertes de vulnérabilité (zones déficitaires)**
  - **Méthode** : `GET`
  - **URL** : `/api/analyses/alertes?campagne_id=3`

- **Évolution du rendement pour une province spécifique**
  - **Méthode** : `GET`
  - **URL** : `/api/analyses/rendement-province/1` *(où 1 est l'id de la province)*

- **Aperçu du rapport texte**
  - **Méthode** : `GET`
  - **URL** : `/api/rapports/preview?campagne_id=3`
