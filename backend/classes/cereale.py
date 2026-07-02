from backend.classes.modele import get_db_connection

class Cereale:
    """
    Classe représentant une Céréale (ex: Sorgho, Maïs).
    Gère les opérations CRUD pour la table `cereales`.
    """
    def __init__(self, id_cereale=None, nom_cereale=None, cycle_maturation=None, besoin_hydrique=None):
        self.id_cereale = id_cereale
        self.nom_cereale = nom_cereale
        self.cycle_maturation = cycle_maturation
        self.besoin_hydrique = besoin_hydrique

    @classmethod
    def get_all(cls):
        """Récupère l'ensemble des céréales de la base de données."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cereales")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @classmethod
    def get_by_id(cls, id_cereale):
        """Récupère une céréale spécifique via son identifiant unique."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cereales WHERE id_cereale = ?", (id_cereale,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def save(self):
        """Enregistre ou met à jour la céréale dans la base de données."""
        conn = get_db_connection()
        cursor = conn.cursor()
        if self.id_cereale:
            cursor.execute('''
                UPDATE cereales 
                SET nom_cereale=?, cycle_maturation=?, besoin_hydrique=? 
                WHERE id_cereale=?
            ''', (self.nom_cereale, self.cycle_maturation, self.besoin_hydrique, self.id_cereale))
        else:
            cursor.execute('''
                INSERT INTO cereales (nom_cereale, cycle_maturation, besoin_hydrique) 
                VALUES (?, ?, ?)
            ''', (self.nom_cereale, self.cycle_maturation, self.besoin_hydrique))
            self.id_cereale = cursor.lastrowid
        conn.commit()
        conn.close()
        return self

    def delete(self):
        """Supprime la céréale de la base de données."""
        if self.id_cereale:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cereales WHERE id_cereale=?", (self.id_cereale,))
            conn.commit()
            conn.close()
