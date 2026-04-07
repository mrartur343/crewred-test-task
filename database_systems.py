import sqlite3

class Database:
    def _get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = 1")
        conn.row_factory = sqlite3.Row
        return conn

    def __init__(self, db_name='database.db'):
        self.db_name = db_name

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS travel_project (
                            name TEXT PRIMARY KEY, 
                            description TEXT, 
                            startdate DATETIME
                        )
                    """)

        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS tp_places (
                            connect_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            tp_name TEXT NOT NULL, 
                            place_id INT NOT NULL, 
                            visited INT DEFAULT 0,
                            FOREIGN KEY(tp_name) REFERENCES travel_project(name) 
                                ON UPDATE CASCADE 
                                ON DELETE CASCADE
                        )
                    """)

        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS place_notes (
                            place_id INT PRIMARY KEY, 
                            place_note TEXT NOT NULL
                        )
                    """)
        connection.commit()
        connection.close()

    # ==========================================
    # Travel Projects Actions
    # ==========================================

    def create_project(self, name, description=None, startdate=None):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO travel_project (name, description, startdate) VALUES (?, ?, ?)",
                (name, description, startdate)
            )
            conn.commit()

    def list_projects(self):
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM travel_project")
            return [dict(row) for row in cursor.fetchall()]

    def get_project(self, name):
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM travel_project WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_project(self, current_name, new_name, description=None, startdate=None):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE travel_project SET name = ?, description = ?, startdate = ? WHERE name = ?",
                (new_name, description, startdate, current_name)
            )
            conn.commit()

    def delete_project(self, name):
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT 1 FROM tp_places WHERE tp_name = ? AND visited = 1", (name,))
            if cursor.fetchone():
                raise ValueError("Cannot delete project: it contains visited places.")

            conn.execute("DELETE FROM travel_project WHERE name = ?", (name,))
            conn.commit()

    # =========================================
    # Places in projects actions
    # =========================================

    def create_project_with_places(self, name, description, startdate, place_ids):
        if len(place_ids) > 10:
            raise ValueError("A project can contain a maximum of 10 places.")

        with self._get_connection() as conn:
            # Створюємо проект
            conn.execute(
                "INSERT INTO travel_project (name, description, startdate) VALUES (?, ?, ?)",
                (name, description, startdate)
            )

            # Фільтруємо дублікати в самому масиві перед вставкою
            unique_places = list(set(place_ids))

            # Додаємо місця
            for place_id in unique_places:
                conn.execute(
                    "INSERT INTO tp_places (tp_name, place_id, visited) VALUES (?, ?, 0)",
                    (name, place_id)
                )
            conn.commit()

    def add_place_to_project(self, tp_name, place_id):
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM tp_places WHERE tp_name = ?", (tp_name,))
            if cursor.fetchone()[0] >= 10:
                raise ValueError("Project already reached the maximum limit of 10 places.")

            cursor = conn.execute("SELECT 1 FROM tp_places WHERE tp_name = ? AND place_id = ?", (tp_name, place_id))
            if cursor.fetchone():
                raise ValueError("This place is already added to the project.")

            conn.execute(
                "INSERT INTO tp_places (tp_name, place_id, visited) VALUES (?, ?, 0)",
                (tp_name, place_id)
            )
            conn.commit()

    def mark_place_visited(self, tp_name, place_id):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE tp_places SET visited = 1 WHERE tp_name = ? AND place_id = ?",
                (tp_name, place_id)
            )
            conn.commit()

    def update_place_note(self, place_id, note):
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO place_notes (place_id, place_note) 
                VALUES (?, ?)
                ON CONFLICT(place_id) DO UPDATE SET place_note=excluded.place_note
            """, (place_id, note))
            conn.commit()

    def list_project_places(self, tp_name):
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT p.place_id, p.visited, n.place_note 
                FROM tp_places p
                LEFT JOIN place_notes n ON p.place_id = n.place_id
                WHERE p.tp_name = ?
            """, (tp_name,))
            return [dict(row) for row in cursor.fetchall()]

    def get_project_place(self, tp_name, place_id):
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT p.place_id, p.visited, n.place_note 
                FROM tp_places p
                LEFT JOIN place_notes n ON p.place_id = n.place_id
                WHERE p.tp_name = ? AND p.place_id = ?
            """, (tp_name, place_id))
            row = cursor.fetchone()
            return dict(row) if row else None