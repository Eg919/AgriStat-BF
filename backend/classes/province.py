from backend.classes.analyseur import get_db_connection

class Province:
    """
    Classe représentant une province.
    Gère les opérations CRUD (Création, Lecture, Mise à jour, Suppression) pour la table `provinces`.
    """
    def __init__(self, id_province=None, id_region=None, nom_province=None, chef_lieu=None, historique_sinistres=None):
        self.id_province = id_province
        self.id_region = id_region
        self.nom_province = nom_province
        self.chef_lieu = chef_lieu
        self.historique_sinistres = historique_sinistres

    @classmethod
    def get_all(cls):
        """Récupère l'ensemble des provinces de la base de données."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM provinces")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @classmethod
    def get_by_id(cls, id_province):
        """Récupère une province spécifique via son identifiant unique."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM provinces WHERE id_province = ?", (id_province,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def save(self):
        """
        Enregistre la province. 
        Mise à jour si la province existe (possède un ID), création dans le cas contraire.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        if self.id_province:
            cursor.execute('''
                UPDATE provinces 
                SET id_region=?, nom_province=?, chef_lieu=?, historique_sinistres=? 
                WHERE id_province=?
            ''', (self.id_region, self.nom_province, self.chef_lieu, self.historique_sinistres, self.id_province))
        else:
            cursor.execute('''
                INSERT INTO provinces (id_region, nom_province, chef_lieu, historique_sinistres) 
                VALUES (?, ?, ?, ?)
            ''', (self.id_region, self.nom_province, self.chef_lieu, self.historique_sinistres))
            self.id_province = cursor.lastrowid
        conn.commit()
        conn.close()
        return self

    def delete(self):
        """Supprime la province de la base de données."""
        if self.id_province:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM provinces WHERE id_province=?", (self.id_province,))
            conn.commit()
            conn.close()
