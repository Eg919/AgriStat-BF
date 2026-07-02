"""
Fichier principal de l'application AgriStat-BF (Backend).
Ce fichier initialise l'application FastAPI, configure les CORS, définit les schémas Pydantic 
et expose tous les endpoints de l'API (Tableau de bord et Opérations CRUD).
"""
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
from classes.region import Region
from classes.province import Province
from classes.cereale import Cereale
from classes.campagne import Campagne
from classes.production import Production

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

# ==========================================
# MODÈLES PYDANTIC
# ==========================================

class RegionCreate(BaseModel):
    nom_region: str
    population_totale: int
    superficie: float

class RegionUpdate(BaseModel):
    nom_region: Optional[str] = None
    population_totale: Optional[int] = None
    superficie: Optional[float] = None

class ProvinceCreate(BaseModel):
    nom_province: str
    id_region: int
    chef_lieu: Optional[str] = None
    historique_sinistres: Optional[str] = None

class ProvinceUpdate(BaseModel):
    nom_province: Optional[str] = None
    id_region: Optional[int] = None
    chef_lieu: Optional[str] = None
    historique_sinistres: Optional[str] = None

class CerealeCreate(BaseModel):
    nom_cereale: str
    cycle_maturation: Optional[str] = None
    besoin_hydrique: Optional[str] = None

class CerealeUpdate(BaseModel):
    nom_cereale: Optional[str] = None
    cycle_maturation: Optional[str] = None
    besoin_hydrique: Optional[str] = None

class CampagneCreate(BaseModel):
    annee: int
    climat_general: Optional[str] = None

class CampagneUpdate(BaseModel):
    annee: Optional[int] = None
    climat_general: Optional[str] = None

class ProductionCreate(BaseModel):
    id_campagne: int
    id_province: int
    id_cereale: int
    superficie_emblavee: float
    quantite_recoltee: float

class ProductionUpdate(BaseModel):
    id_campagne: Optional[int] = None
    id_province: Optional[int] = None
    id_cereale: Optional[int] = None
    superficie_emblavee: Optional[float] = None
    quantite_recoltee: Optional[float] = None


# ==========================================
# ENDPOINTS D'ANALYSE ET TABLEAU DE BORD
# ==========================================

@app.get("/api/dashboard/kpi", tags=["Tableau de bord et Analyses"])
def get_kpi(campagne_id: int = 3): # 3 = Campagne 2025
    stats = analyseur.obtenir_production_totale(campagne_id)
    rendement = analyseur.calculer_rendement_moyen_national(campagne_id)
    return {
        "production_totale": stats["production"],
        "superficie_totale": stats["superficie"],
        "rendement_moyen": rendement
    }

@app.get("/api/dashboard/production-par-region", tags=["Tableau de bord et Analyses"])
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
    return {"labels": labels, "data": data}

@app.get("/api/dashboard/repartition-cereales", tags=["Tableau de bord et Analyses"])
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

@app.get("/api/analyses/alertes", tags=["Tableau de bord et Analyses"])
def get_alertes(campagne_id: int = 3):
    return analyseur.identifier_zones_deficitaires(campagne_id)

@app.get("/api/analyses/rendement-province/{province_id}", tags=["Tableau de bord et Analyses"])
def get_rendement_evolution(province_id: int):
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

@app.get("/api/rapports/preview", tags=["Tableau de bord et Analyses"])
def get_rapport_preview(campagne_id: int = 3):
    texte = analyseur.generer_rapport_kpi(campagne_id)
    return {"rapport": texte}


# ==========================================
# ENDPOINTS DE GESTION (CRUD)
# ==========================================

# ------------------------------------------
# RÉGIONS
# ------------------------------------------
@app.get("/api/gestion/regions", tags=["Régions"])
def get_regions():
    return Region.get_all()

@app.post("/api/gestion/regions", tags=["Régions"])
def create_region(region_data: RegionCreate):
    region = Region(
        nom_region=region_data.nom_region,
        population_totale=region_data.population_totale,
        superficie=region_data.superficie
    )
    try:
        region.save()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Cette région existe déjà")
    return {"message": "Région créée avec succès", "id": region.id_region}

@app.put("/api/gestion/regions/{id}", tags=["Régions"])
def update_region_full(id: int, region_data: RegionCreate):
    region = Region.get_by_id(id)
    if not region: raise HTTPException(status_code=404, detail="Région non trouvée")
    obj = Region(id_region=id, nom_region=region_data.nom_region, population_totale=region_data.population_totale, superficie=region_data.superficie)
    try:
        obj.save()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Erreur d'intégrité : Ce nom de région existe peut-être déjà.")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {e}")
    return {"message": "Région modifiée avec succès"}

@app.patch("/api/gestion/regions/{id}", tags=["Régions"])
def update_region_partial(id: int, region_data: RegionUpdate):
    region = Region.get_by_id(id)
    if not region: raise HTTPException(status_code=404, detail="Région non trouvée")
    obj = Region(id_region=id, nom_region=region_data.nom_region or region['nom_region'], 
                 population_totale=region_data.population_totale or region['population_totale'], 
                 superficie=region_data.superficie or region['superficie'])
    try:
        obj.save()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Erreur d'intégrité : Ce nom de région existe peut-être déjà.")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {e}")
    return {"message": "Région mise à jour avec succès"}

@app.delete("/api/gestion/regions/{id}", tags=["Régions"])
def delete_region(id: int):
    obj = Region(id_region=id)
    try:
        obj.delete()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Impossible de supprimer. Raison : {e}")
    return {"message": "Région supprimée avec succès"}

# ------------------------------------------
# PROVINCES
# ------------------------------------------
@app.get("/api/gestion/provinces", tags=["Provinces"])
def get_provinces():
    return Province.get_all()

@app.post("/api/gestion/provinces", tags=["Provinces"])
def create_province(province_data: ProvinceCreate):
    province = Province(
        id_region=province_data.id_region,
        nom_province=province_data.nom_province,
        chef_lieu=province_data.chef_lieu,
        historique_sinistres=province_data.historique_sinistres
    )
    try:
        province.save()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Cette province existe déjà")
    return {"message": "Province créée avec succès", "id": province.id_province}

@app.put("/api/gestion/provinces/{id}", tags=["Provinces"])
def update_province_full(id: int, data: ProvinceCreate):
    if not Province.get_by_id(id): raise HTTPException(status_code=404, detail="Province non trouvée")
    obj = Province(id_province=id, id_region=data.id_region, nom_province=data.nom_province, chef_lieu=data.chef_lieu, historique_sinistres=data.historique_sinistres)
    try:
        obj.save()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Erreur : Cette province existe déjà ou la région n'existe pas.")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {e}")
    return {"message": "Province modifiée avec succès"}

@app.patch("/api/gestion/provinces/{id}", tags=["Provinces"])
def update_province_partial(id: int, data: ProvinceUpdate):
    exist = Province.get_by_id(id)
    if not exist: raise HTTPException(status_code=404, detail="Province non trouvée")
    obj = Province(id_province=id, 
                   id_region=data.id_region or exist['id_region'], 
                   nom_province=data.nom_province or exist['nom_province'], 
                   chef_lieu=data.chef_lieu or exist['chef_lieu'], 
                   historique_sinistres=data.historique_sinistres or exist['historique_sinistres'])
    try:
        obj.save()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Erreur d'intégrité des données.")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {e}")
    return {"message": "Province mise à jour avec succès"}

@app.delete("/api/gestion/provinces/{id}", tags=["Provinces"])
def delete_province(id: int):
    obj = Province(id_province=id)
    try:
        obj.delete()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Impossible de supprimer. Raison : {e}")
    return {"message": "Province supprimée avec succès"}

# ------------------------------------------
# CÉRÉALES
# ------------------------------------------
@app.get("/api/gestion/cereales", tags=["Céréales"])
def get_cereales():
    return Cereale.get_all()

@app.post("/api/gestion/cereales", tags=["Céréales"])
def create_cereale(cereale_data: CerealeCreate):
    cereale = Cereale(
        nom_cereale=cereale_data.nom_cereale,
        cycle_maturation=cereale_data.cycle_maturation,
        besoin_hydrique=cereale_data.besoin_hydrique
    )
    try:
        cereale.save()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Cette céréale existe déjà")
    return {"message": "Céréale créée avec succès", "id": cereale.id_cereale}

@app.put("/api/gestion/cereales/{id}", tags=["Céréales"])
def update_cereale_full(id: int, data: CerealeCreate):
    if not Cereale.get_by_id(id): raise HTTPException(status_code=404, detail="Céréale non trouvée")
    obj = Cereale(id_cereale=id, nom_cereale=data.nom_cereale, cycle_maturation=data.cycle_maturation, besoin_hydrique=data.besoin_hydrique)
    try:
        obj.save()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Cette céréale existe déjà.")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {e}")
    return {"message": "Céréale modifiée avec succès"}

@app.patch("/api/gestion/cereales/{id}", tags=["Céréales"])
def update_cereale_partial(id: int, data: CerealeUpdate):
    exist = Cereale.get_by_id(id)
    if not exist: raise HTTPException(status_code=404, detail="Céréale non trouvée")
    obj = Cereale(id_cereale=id, nom_cereale=data.nom_cereale or exist['nom_cereale'], 
                  cycle_maturation=data.cycle_maturation or exist['cycle_maturation'], 
                  besoin_hydrique=data.besoin_hydrique or exist['besoin_hydrique'])
    try:
        obj.save()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Erreur d'intégrité des données.")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {e}")
    return {"message": "Céréale mise à jour avec succès"}

@app.delete("/api/gestion/cereales/{id}", tags=["Céréales"])
def delete_cereale(id: int):
    obj = Cereale(id_cereale=id)
    try:
        obj.delete()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Impossible de supprimer. Raison : {e}")
    return {"message": "Céréale supprimée avec succès"}

# ------------------------------------------
# CAMPAGNES
# ------------------------------------------
@app.get("/api/gestion/campagnes", tags=["Campagnes Agricoles"])
def get_campagnes():
    return Campagne.get_all()

@app.post("/api/gestion/campagnes", tags=["Campagnes Agricoles"])
def create_campagne(campagne_data: CampagneCreate):
    campagne = Campagne(
        annee=campagne_data.annee,
        climat_general=campagne_data.climat_general
    )
    try:
        campagne.save()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Cette campagne existe déjà")
    return {"message": "Campagne créée avec succès", "id": campagne.id_campagne}

@app.put("/api/gestion/campagnes/{id}", tags=["Campagnes Agricoles"])
def update_campagne_full(id: int, data: CampagneCreate):
    if not Campagne.get_by_id(id): raise HTTPException(status_code=404, detail="Campagne non trouvée")
    obj = Campagne(id_campagne=id, annee=data.annee, climat_general=data.climat_general)
    try:
        obj.save()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Cette campagne existe déjà.")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {e}")
    return {"message": "Campagne modifiée avec succès"}

@app.patch("/api/gestion/campagnes/{id}", tags=["Campagnes Agricoles"])
def update_campagne_partial(id: int, data: CampagneUpdate):
    exist = Campagne.get_by_id(id)
    if not exist: raise HTTPException(status_code=404, detail="Campagne non trouvée")
    obj = Campagne(id_campagne=id, annee=data.annee or exist['annee'], climat_general=data.climat_general or exist['climat_general'])
    try:
        obj.save()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Erreur d'intégrité des données.")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {e}")
    return {"message": "Campagne mise à jour avec succès"}

@app.delete("/api/gestion/campagnes/{id}", tags=["Campagnes Agricoles"])
def delete_campagne(id: int):
    obj = Campagne(id_campagne=id)
    try:
        obj.delete()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Impossible de supprimer. Raison : {e}")
    return {"message": "Campagne supprimée avec succès"}

# ------------------------------------------
# PRODUCTIONS
# ------------------------------------------
@app.get("/api/gestion/productions", tags=["Productions"])
def get_productions():
    return Production.get_all()

@app.post("/api/gestion/productions", tags=["Productions"])
def create_production(prod_data: ProductionCreate):
    production = Production(
        id_campagne=prod_data.id_campagne,
        id_province=prod_data.id_province,
        id_cereale=prod_data.id_cereale,
        superficie_emblavee=prod_data.superficie_emblavee,
        quantite_recoltee=prod_data.quantite_recoltee
    )
    try:
        production.save()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Vérifiez que la campagne, la province et la céréale existent.")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {e}")
    return {"message": "Production enregistrée avec succès", "id": production.id_production}

@app.put("/api/gestion/productions/{id}", tags=["Productions"])
def update_production_full(id: int, data: ProductionCreate):
    if not Production.get_by_id(id): raise HTTPException(status_code=404, detail="Production non trouvée")
    obj = Production(id_production=id, id_campagne=data.id_campagne, id_province=data.id_province, id_cereale=data.id_cereale, superficie_emblavee=data.superficie_emblavee, quantite_recoltee=data.quantite_recoltee)
    try:
        obj.save()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Vérifiez que la campagne, la province et la céréale existent.")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {e}")
    return {"message": "Production modifiée avec succès"}

@app.patch("/api/gestion/productions/{id}", tags=["Productions"])
def update_production_partial(id: int, data: ProductionUpdate):
    exist = Production.get_by_id(id)
    if not exist: raise HTTPException(status_code=404, detail="Production non trouvée")
    obj = Production(id_production=id, 
                     id_campagne=data.id_campagne or exist['id_campagne'], 
                     id_province=data.id_province or exist['id_province'], 
                     id_cereale=data.id_cereale or exist['id_cereale'], 
                     superficie_emblavee=data.superficie_emblavee or exist['superficie_emblavee'], 
                     quantite_recoltee=data.quantite_recoltee or exist['quantite_recoltee'])
    try:
        obj.save()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Vérifiez que les clés étrangères existent.")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {e}")
    return {"message": "Production mise à jour avec succès"}

@app.delete("/api/gestion/productions/{id}", tags=["Productions"])
def delete_production(id: int):
    obj = Production(id_production=id)
    try:
        obj.delete()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Impossible de supprimer. Raison : {e}")
    return {"message": "Production supprimée avec succès"}

# Lancement serveur local : uvicorn main:app --reload
