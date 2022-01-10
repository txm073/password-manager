import sqlite3
import os, sys, re
import shutil
import string as _string
import hashlib
import random
import utils

from PyQt5.QtWidgets import *


class Manager:

    CHARS = _string.printable + "£"
    STOR_CHAR = {c: i for i, c in enumerate(CHARS)}
    RETR_CHAR = {i: c for i, c in enumerate(CHARS)}
    DELIM_CHAR = "Ö"

    def __init__(self, db_path, master_pass, enc_key):
        self.db_path = db_path
        self.master_pass = master_pass
        self.enc_key = enc_key
        if not self.authenticate(master_pass):
            raise utils.AuthenticationError(
                "Master password is invalid!"
            )
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        cmd = \
        """
        CREATE TABLE IF NOT EXISTS passwords (
            site TEXT,
            username TEXT,
            password TEXT
        )
        """
        self.cursor.execute(cmd)
        
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.conn.commit()

    def authenticate(self, password):
        with open("master.rtf", "r") as f:
            password = hashlib.sha3_256(
                utils.encrypt(password, password, len(password)).encode()
            ).hexdigest()
            return password == str(f.read()).strip()
            
    @staticmethod
    def create_password(length=16, lower=True, upper=True, nums=True, symbols=True):
        options = [lower, upper, nums, symbols]
        if not any(options):
            raise ValueError(
                "Select an argument as True: lowercase, uppercase, numbers, symbols"
            )
        total = ""
        if lower:
            total += _string.ascii_lowercase
        if upper:
            total += _string.ascii_uppercase
        if nums:
            total += _string.digits
        if symbols:
            total += "#_+/=*&^%$£"
        secure_random = random.SystemRandom()
        return "".join([secure_random.choice(total) for i in range(length)])        

    def change_password(self, site, password):
        pass

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
        assert self.fetch(site)[0] != site, f"Information already exists for site '{site}'"
        info = (
            self._convert_to_storage(site),
            self._convert_to_storage(username),
            self._convert_to_storage(utils.encrypt(password, self.enc_key, len(self.enc_key)))
        )
        self.cursor.execute("""INSERT INTO passwords VALUES (?, ?, ?)""", info)

    def fetch(self, site, decrypt=True):
        if decrypt:
            row = [self._convert_from_storage(col) for col in self.fetch_most_likely(site)]
            return row[0], row[1], utils.decrypt(row[2], self.enc_key, len(self.enc_key)) if row[2] is not None else None
        return tuple([self._convert_from_storage(col) for col in self.fetch_most_likely(site)])

    def fetch_sites(self):
        self.cursor.execute("""SELECT site FROM passwords""")
        return [self._convert_from_storage(result[0]) for result in self.cursor.fetchall()]

    def fetch_most_likely(self, target, col="site"):
        sites = self.fetch_sites()
        site = utils.most_likely(sites, target)
        if site is None:
            return None, None, None
        self.cursor.execute(f"""SELECT * FROM passwords WHERE {col}='{self._convert_to_storage(site)}'""")
        return self.cursor.fetchone()

    def _convert_to_storage(self, string):
        return self.DELIM_CHAR.join([str(self.STOR_CHAR[char]) for char in string])

    def _convert_from_storage(self, string):
        return "".join([self.RETR_CHAR[int(i)] for i in string.split(self.DELIM_CHAR)]) if string else None

    @utils.threaded(0)
    def gui(self, data):
        app = QApplication(sys.argv)
        win = GUI(data)
        win.show()
        sys.exit(app.exec_())


class GUI(QDialog):

    width, height = 900, 450
    headers = ["Site", "Username", "Password"]

    def __init__(self, data):
        self.data = data
        super().__init__()
        self.table = QTableWidget(5, len(self.headers), self)
        self.table.resize(self.width, self.height)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setRowCount(len(self.data) + 1)
        for i in range(len(self.headers)):
            self.table.setColumnWidth(i, self.width // len(self.headers) - 1)
            self.table.setItem(0, i, QTableWidgetItem(self.headers[i]))
        for i, row in enumerate(self.data, 1):
            for j, col in enumerate(row):
                if j == 2:
                    self.table.setCellWidget(i, j, self.button(str(col)))
                else:
                    self.table.setItem(i, j, QTableWidgetItem(str(col)))

    def btn_click(self, text, label, check):
        def _click():
            check.setText(text)
        return _click

    def button(self, text):
        frame = QFrame()
        layout = QHBoxLayout()
        label = QLabel(text)
        check = QCheckBox()
        check.stateChanged.connect(lambda: self.btn_click(text, label, check))

        layout.addWidget(label)
        layout.addWidget(check)
        frame.setLayout(layout)
        return frame
    

if __name__ == "__main__": 
    with Manager("database.db", "scrumptiouspar_celenzyme", "qdh5ykmtDrpjf4phPskLnx4k") as manager:
        #manager.add("Reddit", "tom.barnes1_", manager.create_password())
        print(manager.fetch("instagram", decrypt=True))
        