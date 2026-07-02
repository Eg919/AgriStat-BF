from backend.classes.modele import get_db_connection

class Region:
    """
    Classe représentant une région dans l'application AgriStat-BF.
    Permet de manipuler les données des régions via des méthodes CRUD en interagissant avec la base de données SQLite.
    """
    def __init__(self, id_region=None, nom_region=None, population_totale=None, superficie=None):
        self.id_region = id_region
        self.nom_region = nom_region
        self.population_totale = population_totale
        self.superficie = superficie

    @classmethod
    def get_all(cls):
        """
        Récupère toutes les régions enregistrées dans la base de données.
        :return: Une liste de dictionnaires représentant chaque région.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM regions")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @classmethod
    def get_by_id(cls, id_region):
        """
        Récupère une région spécifique par son identifiant.
        :param id_region: L'identifiant unique de la région.
        :return: Un dictionnaire contenant les données de la région, ou None si non trouvée.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM regions WHERE id_region = ?", (id_region,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def save(self):
        """
        Sauvegarde la région dans la base de données.
        Si l'objet a déjà un id_region, effectue une mise à jour (UPDATE).
        Sinon, insère une nouvelle région (INSERT) et récupère l'ID généré.
        :return: L'instance de la région sauvegardée.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        if self.id_region:
            # Mise à jour si l'ID existe déjà
            cursor.execute('''
                UPDATE regions 
                SET nom_region=?, population_totale=?, superficie=? 
                WHERE id_region=?
            ''', (self.nom_region, self.population_totale, self.superficie, self.id_region))
        else:
            # Création si c'est une nouvelle région
            cursor.execute('''
                INSERT INTO regions (nom_region, population_totale, superficie) 
                VALUES (?, ?, ?)
            ''', (self.nom_region, self.population_totale, self.superficie))
            self.id_region = cursor.lastrowid
        conn.commit()
        conn.close()
        return self

    def delete(self):
        """
        Supprime cette région de la base de données de façon définitive.
        """
        if self.id_region:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM regions WHERE id_region=?", (self.id_region,))
            conn.commit()
            conn.close()
