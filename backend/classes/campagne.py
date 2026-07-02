from backend.classes.analyseur import get_db_connection

class Campagne:
    """
    Classe représentant une Campagne agricole (une saison/année spécifique).
    Gère les opérations CRUD pour la table `campagnes`.
    """
    def __init__(self, id_campagne=None, annee=None, climat_general=None):
        self.id_campagne = id_campagne
        self.annee = annee
        self.climat_general = climat_general

    @classmethod
    def get_all(cls):
        """Récupère l'ensemble des campagnes agricoles."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM campagnes")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @classmethod
    def get_by_id(cls, id_campagne):
        """Récupère une campagne spécifique par son ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM campagnes WHERE id_campagne = ?", (id_campagne,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def save(self):
        """Enregistre ou met à jour la campagne dans la base de données."""
        conn = get_db_connection()
        cursor = conn.cursor()
        if self.id_campagne:
            cursor.execute('''
                UPDATE campagnes 
                SET annee=?, climat_general=? 
                WHERE id_campagne=?
            ''', (self.annee, self.climat_general, self.id_campagne))
        else:
            cursor.execute('''
                INSERT INTO campagnes (annee, climat_general) 
                VALUES (?, ?)
            ''', (self.annee, self.climat_general))
            self.id_campagne = cursor.lastrowid
        conn.commit()
        conn.close()
        return self

    def delete(self):
        """Supprime la campagne de la base de données."""
        if self.id_campagne:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM campagnes WHERE id_campagne=?", (self.id_campagne,))
            conn.commit()
            conn.close()
