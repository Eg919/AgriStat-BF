from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes.modele import AnalyseurStatistique, get_db_connection

app = FastAPI(title="AgriStat-BF API", description="API pour la plateforme AgriStat-BF")

# Configuration CORS pour permettre au frontend d'appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier l'origine exacte
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyseur = AnalyseurStatistique()

# --- Modèles Pydantic pour les requêtes POST ---
class ProvinceCreate(BaseModel):
    nom_province: str
    population_totale: int
    superficie: float
    id_region: int = 1 # Par défaut, on l'associe à la région 1 pour simplifier

class ProductionCreate(BaseModel):
    id_campagne: int
    id_province: int
    id_cereale: int
    superficie_emblavee: float
    quantite_recoltee: float

# --- Endpoints ---

@app.get("/api/dashboard/kpi")
def get_kpi(campagne_id: int = 3): # 3 = Campagne 2025
    stats = analyseur.obtenir_production_totale(campagne_id)
    rendement = analyseur.calculer_rendement_moyen_national(campagne_id)
    return {
        "production_totale": stats["production"],
        "superficie_totale": stats["superficie"],
        "rendement_moyen": rendement
    }

@app.get("/api/dashboard/production-par-region")
def get_production_by_region(campagne_id: int = 3):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.nom_region, SUM(p.quantite_recoltee) as total_prod
        FROM productions p
        JOIN provinces pr ON p.id_province = pr.id_province
        JOIN regions r ON pr.id_region = r.id_region
        WHERE p.id_campagne = ?
        GROUP BY r.id_region
    ''', (campagne_id,))
    
    labels = []
    data = []
    for row in cursor.fetchall():
        labels.append(row['nom_region'])
        data.append(row['total_prod'] or 0)
    conn.close()
    
    # S'il n'y a pas assez de données (ex: SQLite de démo), on complète avec des 0 pour les autres régions
    return {"labels": labels, "data": data}

@app.get("/api/dashboard/repartition-cereales")
def get_cereales_distribution(campagne_id: int = 3):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.nom_cereale, SUM(p.quantite_recoltee) as total_prod
        FROM productions p
        JOIN cereales c ON p.id_cereale = c.id_cereale
        WHERE p.id_campagne = ?
        GROUP BY c.id_cereale
    ''', (campagne_id,))
    
    labels = []
    data = []
    for row in cursor.fetchall():
        labels.append(row['nom_cereale'])
        data.append(row['total_prod'] or 0)
    conn.close()
    return {"labels": labels, "data": data}

@app.get("/api/analyses/alertes")
def get_alertes(campagne_id: int = 3):
    return analyseur.identifier_zones_deficitaires(campagne_id)

@app.get("/api/analyses/rendement-province/{province_id}")
def get_rendement_evolution(province_id: int):
    # Simuler l'évolution sur les 5 dernières années
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.annee, (p.quantite_recoltee / p.superficie_emblavee) as rendement
        FROM productions p
        JOIN campagnes c ON p.id_campagne = c.id_campagne
        WHERE p.id_province = ? AND p.superficie_emblavee > 0
        ORDER BY c.annee ASC
    ''', (province_id,))
    
    annees = []
    rendements_prov = []
    for row in cursor.fetchall():
        annees.append(str(row['annee']))
        rendements_prov.append(round(row['rendement'], 2))
    conn.close()
    
    return {
        "labels": annees,
        "province": rendements_prov,
        "region_moyenne": [2.0, 2.1, 1.8, 2.2, 2.02] # Simulée
    }

@app.get("/api/rapports/preview")
def get_rapport_preview(campagne_id: int = 3):
    texte = analyseur.generer_rapport_kpi(campagne_id)
    return {"rapport": texte}

@app.post("/api/gestion/provinces")
def create_province(province: ProvinceCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO provinces (nom_province, id_region, chef_lieu, historique_sinistres)
            VALUES (?, ?, ?, ?)
        ''', (province.nom_province, province.id_region, 'N/A', ''))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Cette province existe déjà")
    finally:
        conn.close()
    return {"message": "Province créée avec succès"}

@app.post("/api/gestion/productions")
def create_production(prod: ProductionCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO productions (id_campagne, id_province, id_cereale, superficie_emblavee, quantite_recoltee)
        VALUES (?, ?, ?, ?, ?)
    ''', (prod.id_campagne, prod.id_province, prod.id_cereale, prod.superficie_emblavee, prod.quantite_recoltee))
    conn.commit()
    conn.close()
    return {"message": "Production enregistrée avec succès"}

# Lancement serveur local : uvicorn main:app --reload
