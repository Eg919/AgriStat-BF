import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'agristat.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class AnalyseurStatistique:
    def __init__(self):
        pass
        
    def calculer_rendement_moyen_national(self, id_campagne):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(quantite_recoltee) / SUM(superficie_emblavee) as rendement_moyen 
            FROM productions 
            WHERE id_campagne = ? AND superficie_emblavee > 0
        ''', (id_campagne,))
        result = cursor.fetchone()
        conn.close()
        return round(result['rendement_moyen'], 2) if result and result['rendement_moyen'] else 0.0

    def obtenir_production_totale(self, id_campagne):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(quantite_recoltee) as totale, SUM(superficie_emblavee) as surf_totale
            FROM productions 
            WHERE id_campagne = ?
        ''', (id_campagne,))
        result = cursor.fetchone()
        conn.close()
        return {
            "production": result['totale'] or 0,
            "superficie": result['surf_totale'] or 0
        }

    def identifier_zones_deficitaires(self, id_campagne):
        conn = get_db_connection()
        cursor = conn.cursor()
        # Simulation d'un calcul de taux de couverture : 
        # (Production / (Population de la province * 0.190)) * 100  -- 190kg/habitant/an
        cursor.execute('''
            SELECT p.nom_province, r.nom_region, 
                   SUM(prod.quantite_recoltee) as prod_totale,
                   p.historique_sinistres
            FROM provinces p
            JOIN regions r ON p.id_region = r.id_region
            JOIN productions prod ON prod.id_province = p.id_province
            WHERE prod.id_campagne = ?
            GROUP BY p.id_province
        ''', (id_campagne,))
        
        zones = []
        for row in cursor.fetchall():
            # Valeurs simulées pour la démo car on n'a pas la population par province dans le schéma (seulement région)
            # On simule un taux de couverture basé sur le rendement
            prod = row['prod_totale']
            # On va dire que si prod < 50000 c'est critique
            taux = min(100, int((prod / 100000) * 100)) if prod else 0
            statut = "Critique" if taux < 60 else "Alerte" if taux < 80 else "Normal"
            
            if statut != "Normal":
                zones.append({
                    "province": row['nom_province'],
                    "region": row['nom_region'],
                    "taux_couverture": f"{taux}%",
                    "historique": row['historique_sinistres'],
                    "statut": statut
                })
        conn.close()
        return zones

    def generer_rapport_kpi(self, id_campagne):
        # Cette méthode génère le texte brut pour le rapport
        stats = self.obtenir_production_totale(id_campagne)
        rendement = self.calculer_rendement_moyen_national(id_campagne)
        zones = self.identifier_zones_deficitaires(id_campagne)
        
        # Obtenir l'année
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT annee FROM campagnes WHERE id_campagne = ?', (id_campagne,))
        annee_res = cursor.fetchone()
        annee = annee_res['annee'] if annee_res else "Inconnue"
        
        # Obtenir répartition
        cursor.execute('''
            SELECT c.nom_cereale, SUM(p.quantite_recoltee) as qty
            FROM productions p
            JOIN cereales c ON p.id_cereale = c.id_cereale
            WHERE p.id_campagne = ?
            GROUP BY c.id_cereale
        ''', (id_campagne,))
        cereales_repart = cursor.fetchall()
        conn.close()

        rapport = f"==================================================\n"
        rapport += f"RAPPORT KPI - CAMPAGNE AGRICOLE {annee}\n"
        rapport += f"==================================================\n\n"
        
        rapport += f"[1] INDICATEURS GLOBAUX\n"
        rapport += f"--------------------------------------------------\n"
        rapport += f"- Production Totale : {stats['production']:,.0f} Tonnes\n"
        rapport += f"- Superficie Emblavée : {stats['superficie']:,.0f} Hectares\n"
        rapport += f"- Rendement Moyen National : {rendement} T/Ha\n\n"
        
        rapport += f"[2] REPARTITION PAR CEREALE\n"
        rapport += f"--------------------------------------------------\n"
        totale_prod = stats['production'] if stats['production'] > 0 else 1
        for c in cereales_repart:
            pct = (c['qty'] / totale_prod) * 100
            rapport += f"- {c['nom_cereale']:<6} : {c['qty']:,.0f} T ({pct:.0f}%)\n"
            
        rapport += f"\n[3] ALERTES DE VULNERABILITE (ZONES ROUGES)\n"
        rapport += f"--------------------------------------------------\n"
        if not zones:
            rapport += "Aucune zone critique identifiée.\n"
        for z in zones:
            rapport += f"* Province du {z['province']} (Taux: {z['taux_couverture']}) - {z['statut'].upper()}\n"
            
        rapport += f"\n==================================================\n"
        return rapport
