import sqlite3
import os
import hashlib

def init_db():
    # S'assurer que le dossier existe
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    db_path = os.path.join(os.path.dirname(__file__), 'agristat.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Création des tables
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS regions (
        id_region INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_region TEXT UNIQUE NOT NULL,
        population_totale INTEGER,
        superficie REAL
    );

    CREATE TABLE IF NOT EXISTS provinces (
        id_province INTEGER PRIMARY KEY AUTOINCREMENT,
        id_region INTEGER,
        nom_province TEXT UNIQUE NOT NULL,
        chef_lieu TEXT,
        historique_sinistres TEXT,
        FOREIGN KEY (id_region) REFERENCES regions (id_region)
    );

    CREATE TABLE IF NOT EXISTS cereales (
        id_cereale INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_cereale TEXT UNIQUE NOT NULL,
        cycle_maturation TEXT,
        besoin_hydrique TEXT
    );

    CREATE TABLE IF NOT EXISTS campagnes (
        id_campagne INTEGER PRIMARY KEY AUTOINCREMENT,
        annee INTEGER UNIQUE NOT NULL,
        climat_general TEXT
    );

    CREATE TABLE IF NOT EXISTS productions (
        id_production INTEGER PRIMARY KEY AUTOINCREMENT,
        id_campagne INTEGER,
        id_province INTEGER,
        id_cereale INTEGER,
        superficie_emblavee REAL,
        quantite_recoltee REAL,
        FOREIGN KEY (id_campagne) REFERENCES campagnes (id_campagne),
        FOREIGN KEY (id_province) REFERENCES provinces (id_province),
        FOREIGN KEY (id_cereale) REFERENCES cereales (id_cereale)
    );

    CREATE TABLE IF NOT EXISTS users (
        id_user INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('analyste', 'visualisateur'))
    );
    """)

    # Insertion des comptes utilisateurs par défaut
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        def sha256(password: str) -> str:
            return hashlib.sha256(password.encode()).hexdigest()

        default_users = [
            ('admin',  sha256('agristat2025'), 'analyste'),
            ('viewer', sha256('viewer123'),    'visualisateur'),
        ]
        cursor.executemany(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            default_users
        )
        print("Comptes utilisateurs par défaut créés : admin / viewer")

    # Insertion de données initiales (si la base est vide)
    cursor.execute("SELECT COUNT(*) FROM regions")
    if cursor.fetchone()[0] == 0:
        print("Insertion des données de démonstration...")
        # Régions
        regions = [
            ('Boucle du Mouhoun', 1500000, 34153),
            ('Hauts-Bassins', 1800000, 25344),
            ('Centre', 2500000, 2805),
            ('Nord', 1200000, 16202),
            ('Sahel', 1100000, 35350),
            ('Est', 1400000, 46256)
        ]
        cursor.executemany("INSERT INTO regions (nom_region, population_totale, superficie) VALUES (?, ?, ?)", regions)

        # Provinces (exemples)
        provinces = [
            (1, 'Kossi', 'Nouna', 'Inondation 2022'),
            (2, 'Houet', 'Bobo-Dioulasso', ''),
            (3, 'Kadiogo', 'Ouagadougou', ''),
            (4, 'Loroum', 'Titao', 'Sécheresse 2023, 2024'),
            (5, 'Soum', 'Djibo', 'Sécheresse 2023'),
            (6, 'Gourma', 'Fada N\'Gourma', 'Sécheresse 2024')
        ]
        cursor.executemany("INSERT INTO provinces (id_region, nom_province, chef_lieu, historique_sinistres) VALUES (?, ?, ?, ?)", provinces)

        # Céréales
        cereales = [
            ('Sorgho', 'Moyen', 'Faible'),
            ('Maïs', 'Court', 'Elevé'),
            ('Mil', 'Court', 'Faible'),
            ('Riz', 'Long', 'Très Elevé')
        ]
        cursor.executemany("INSERT INTO cereales (nom_cereale, cycle_maturation, besoin_hydrique) VALUES (?, ?, ?)", cereales)

        # Campagnes
        campagnes = [
            (2023, 'Déficitaire'),
            (2024, 'Moyen'),
            (2025, 'Bon')
        ]
        cursor.executemany("INSERT INTO campagnes (annee, climat_general) VALUES (?, ?)", campagnes)

        # Productions (Campagne 2025, id=3)
        # (id_campagne, id_province, id_cereale, superficie_emblavee, quantite_recoltee)
        productions = [
            (3, 1, 1, 50000, 95000),  # Kossi, Sorgho (Rendement ~1.9)
            (3, 2, 2, 80000, 200000), # Houet, Maïs (Rendement 2.5)
            (3, 4, 3, 30000, 25000),  # Loroum, Mil (Rendement ~0.8) - Déficitaire
            (3, 5, 3, 25000, 15000),  # Soum, Mil (Rendement 0.6) - Déficitaire
            (3, 6, 1, 45000, 60000),  # Gourma, Sorgho (Rendement ~1.3)
            # Historique pour le graphique
            (2, 2, 2, 75000, 157500), # 2024, Houet, Maïs (2.1)
            (1, 2, 2, 70000, 98000),  # 2023, Houet, Maïs (1.4)
        ]
        cursor.executemany("INSERT INTO productions (id_campagne, id_province, id_cereale, superficie_emblavee, quantite_recoltee) VALUES (?, ?, ?, ?, ?)", productions)

    conn.commit()
    conn.close()
    print("Base de données initialisée avec succès.")

if __name__ == "__main__":
    init_db()
