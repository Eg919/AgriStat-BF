try:
    from backend.classes.modele import get_db_connection
except ImportError:
    from classes.modele import get_db_connection

class Production:
    """
    Classe représentant les données de Production agricole pour une céréale donnée, 
    dans une province donnée, lors d'une campagne donnée.
    Gère les opérations CRUD pour la table `productions`.
    """
    def __init__(self, id_production=None, id_campagne=None, id_province=None, id_cereale=None, superficie_emblavee=None, quantite_recoltee=None):
        self.id_production = id_production
        self.id_campagne = id_campagne
        self.id_province = id_province
        self.id_cereale = id_cereale
        self.superficie_emblavee = superficie_emblavee
        self.quantite_recoltee = quantite_recoltee

    @classmethod
    def get_all(cls):
        """Récupère tous les enregistrements de production."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productions")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @classmethod
    def get_by_id(cls, id_production):
        """Récupère une production spécifique."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productions WHERE id_production = ?", (id_production,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def save(self):
        """Enregistre ou met à jour les données de production."""
        conn = get_db_connection()
        cursor = conn.cursor()
        if self.id_production:
            cursor.execute('''
                UPDATE productions 
                SET id_campagne=?, id_province=?, id_cereale=?, superficie_emblavee=?, quantite_recoltee=? 
                WHERE id_production=?
            ''', (self.id_campagne, self.id_province, self.id_cereale, self.superficie_emblavee, self.quantite_recoltee, self.id_production))
        else:
            cursor.execute('''
                INSERT INTO productions (id_campagne, id_province, id_cereale, superficie_emblavee, quantite_recoltee) 
                VALUES (?, ?, ?, ?, ?)
            ''', (self.id_campagne, self.id_province, self.id_cereale, self.superficie_emblavee, self.quantite_recoltee))
            self.id_production = cursor.lastrowid
        conn.commit()
        conn.close()
        return self

    def delete(self):
        """Supprime cet enregistrement de production."""
        if self.id_production:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productions WHERE id_production=?", (self.id_production,))
            conn.commit()
            conn.close()
