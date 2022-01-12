import sqlite3, re, json
from base64 import b64encode, b64decode


class Manager:

    def __init__(self, master):
        self.master = master
        self.db = sqlite3.connect("passwords.db")
        self.conn = self.db.cursor()
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS passwords (
                site TEXT,
                username TEXT,
                password TEXT,
                info TEXT
            )
            """
        )

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.db.close()

    def _convert(self, data):
        if type(data) is dict:
            data = json.dumps(data)
        return b64encode(data.encode()).decode() 

    def validate_input(self, string):
        commands = [
            "ALTER TABLE ", "BETWEEN ", "CREATE TABLE ", "DELETE ", "DROP " 
            "INNER JOIN ", "INSERT ", "INTO ", "IS NULL ", "IS NOT NULL ", "OUTER JOIN ", 
            "SELECT ", "SELECT DISTINCT ", "UPDATE ", "UNION ", "WHERE ", "WITH ", "VALUES"
        ]
        syntax = ["'\)", "\-\-"]
        for elem in syntax + commands:
            if re.search(elem, string):
                return False
        return True    

    def add(self, site, username, password, **info):
        data = (
            self._convert(site), 
            self._convert(username),
            self._convert(password),
            self._convert(info)
        )
        cmd = f"INSERT INTO passwords VALUES {str(data)}"
        self.conn.execute(cmd)
        self.db.commit()

    def remove(self, site):
        pass

    def fetch(self, site):
        self.conn.execute(f"SELECT * FROM passwords WHERE site = '{self._convert(site)}'")
        return self.conn.fetchall()


if __name__ == "__main__":
    with Manager("master-password") as manager:
        #manager.add("Instagram", "tom.barnes1_", "1234")
        print(manager.fetch("Instagram"))
