import sqlite3

class Database:
    def __init__(self):
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
