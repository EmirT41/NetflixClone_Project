import pyodbc


class DatabaseConnection:
    def __init__(self):
        self.conn = pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=localhost;"
            "DATABASE=FilmDB;"
            "Trusted_Connection=yes;"
        )

    def getCursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()
