import sqlite3
import os

# Chemin absolu vers la base de données, peu importe d'où le script est lancé
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'agristat.db')

def get_db_connection():
    """Crée et retourne une connexion à la base de données SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class AnalyseurStatistique:
    """
    Classe responsable de l'analyse statistique des données de production agricole.
    Fournit des méthodes pour calculer des KPIs, identifier les zones déficitaires
    et générer des rapports textuels.
    """
    def __init__(self):
        pass
        
    def calculer_rendement_moyen_national(self, id_campagne):
        """
        Calcule le rendement moyen national (T/Ha) pour une campagne donnée.
        :param id_campagne: L'identifiant de la campagne agricole.
        :return: Le rendement moyen arrondi à 2 décimales.
        """
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
        """
        Retourne la production totale et la superficie totale emblavée pour une campagne.
        :param id_campagne: L'identifiant de la campagne agricole.
        :return: Un dictionnaire avec les clés 'production' et 'superficie'.
        """
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
        """
        Identifie les provinces en situation de déficit alimentaire pour une campagne donnée.
        Une province est considérée en alerte si son taux de couverture est inférieur à 80%.
        :param id_campagne: L'identifiant de la campagne agricole.
        :return: Une liste de dictionnaires décrivant chaque zone vulnérable.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
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
            prod = row['prod_totale']
            # Taux de couverture simulé : < 50 000 T = critique, < 80 000 T = alerte
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
        """
        Génère un rapport textuel complet avec les KPIs de la campagne.
        :param id_campagne: L'identifiant de la campagne agricole.
        :return: Une chaîne de caractères formatée représentant le rapport.
        """
        stats = self.obtenir_production_totale(id_campagne)
        rendement = self.calculer_rendement_moyen_national(id_campagne)
        zones = self.identifier_zones_deficitaires(id_campagne)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT annee FROM campagnes WHERE id_campagne = ?', (id_campagne,))
        annee_res = cursor.fetchone()
        annee = annee_res['annee'] if annee_res else "Inconnue"
        
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
