import sys
import string
import secrets
import mysql.connector
from PyQt5.QtWidgets import *
import threading
import webbrowser
import pyperclip
import time
import re
import os

os.chdir(os.path.dirname(__file__))
from utils import encrypt, decrypt

# Connect to remote database
class Connection:

    # DO NOT MODIFY STRING!!!
    secure_username = """?Eet^IiQLKy~NZiFSlqrT5WMh2%67vNNp9#"&$y;):"I&:K_J"W&)T^0:}0-__=b@~+e]8#fj$[!m*q]j_+.&dbV/f[^v[}gIMVVCRQh`LblaEYoZAvlZrC'5I&Q!TDv5W<uzG.'*MX)<@?Z"""
    secure_password = """?Eet^IqzLzqHPCi)SlqrQ5RDZ8!xYvO*pTZD&$y;90OWFK&\J"W&)T^0:}ZX?c@!@a.k48#4i$@v#*.tjs_.gta/,iEFE[b`J}VNCvQh`LblaEYoZAvlZrC'5I&Q!TDv5W<uzG.'*MX)<@?Z"""

    # Master passwords
    def __init__(self, master_password, encryption_key):
        self.master_key = encrypt(master_password, encryption_key)
        
        auth_failed = False
        try:
            self.user = decrypt(self.secure_username, self.master_key, layers=len(self.master_key) // 4)
            self.password = decrypt(self.secure_password, self.master_key, layers=len(self.master_key) // 4)
        
        except Exception: 
            raise Exception(
                "Incorrect password or encryption key."
            ) from None

        print("Successfully authenticated")
        self.database = decrypt("""Wv'$#"xN4YY,wTjk""", "passwords")
        
        try:
            self.sql = mysql.connector.connect(
                host="remotemysql.com",
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("Successfully accessed database")
        except:
            print("Unable to connect to remote database")
            sys.exit()

        self.conn = self.sql.cursor()
        #self.conn.execute("DROP TABLE data")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS data 
                                    (
                                    site TEXT, 
                                    link TEXT, 
                                    email TEXT, 
                                    phone TEXT, 
                                    username TEXT, 
                                    password TEXT
                                    )""")    
                                    
    def show_table(self):
        self.conn.execute("SELECT * FROM data")
        data = self.conn.fetchall()
        
        thread = threading.Thread(target=self._gui, args=(data, ))
        thread.start()
    
    def _gui(self, data):    
        app = QApplication(sys.argv)
        
        win = TableWindow(headers=["Website", "Link", "Email", "Phone", "Username", "Password"], 
                            data=data)
        sys.exit(app.exec_())

    def validate_input(self, string):
        commands = [
            "ALTER TABLE ", "BETWEEN ", "CREATE TABLE ", "DELETE ", "DROP " 
            "INNER JOIN ", "INSERT ", "INTO ", "IS NULL ", "IS NOT NULL ", "OUTER JOIN ", 
            "SELECT ", "SELECT DISTINCT ", "UPDATE ", "WHERE ", "WITH ", "VALUES"
                ]

        syntax = ["'\)", "\-\-"]
        for elem in syntax + commands:
            if re.search(elem, string):
                return False
        return True

    def login_with(self, site):
        row = self.fetch(site)
        if row is None:
            return row
        url = row[1]
        password = row[-1]
        webbrowser.open_new_tab(url)
        pyperclip.copy(password)

    def fetch(self, site):
        self.conn.execute(f"SELECT * FROM data WHERE site='{site}'")
        return self.conn.fetchone()

    def add(self, site="None", link="None", email="None", 
                phone="None", username="None", password="None"):
        
        if self.fetch(site):
            print("Site already exists in the database")
            return None 

        params = [site, link, email, phone, username, password]
        
        for elem in params:
            if not self.validate_input(elem):
                print(f"Invalid character found in '{elem}'")
                return None

        data = ",".join([f"'{elem}'" for elem in params])

        self.conn.execute(f"INSERT INTO data VALUES({data})")

    def _reset(self):
        self.conn.execute("DROP TABLE data")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS data 
                                    (
                                    site TEXT, 
                                    link TEXT, 
                                    email TEXT, 
                                    phone TEXT, 
                                    username TEXT, 
                                    password TEXT
                                    )""")    
        self.save()

    def columns(self):
        self.conn.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = 'data'")
        return self.conn.fetchone()[0]

    def modify(self, site, column, new):
        row = self.fetch(site)
        columns = ["site", "link", "email", "phone", "username", "password"]

        if row is None or column not in columns:
            return None

        self.conn.execute(f"UPDATE data SET {column}='{new}' WHERE site='{site}'")
        self.save()

    def save(self):
        self.sql.commit()
    
    def close(self):
        self.sql.close()

    @classmethod
    def generate_password(cls, length=16, lower=True, upper=True, nums=True, symbols=True):
        options = [lower, upper, nums, symbols]
        if not any(options):
            return None
        
        total = ""
        if lower:
            total += string.ascii_lowercase
        if upper:
            total += string.ascii_uppercase
        if nums:
            total += string.digits
        if symbols:
            total += "#_+/=*&^%$£"

        secure_random = secrets.SystemRandom()
        return "".join([secure_random.choice(total) for i in range(length)])        

    def commands(self):
        while True:
            command = input("\nEnter a command >>> ")
            if command.startswith("modify"):
                site = command[len("modify"):]
                if not site.strip():
                    print("You must specify a site!")
                    continue
                data_type = input(f"Enter detail you would like to edit from {site}: ")
                new = input(f"Enter new {data_type} for {site}: ")
                self.modify(site, data_type, new)
                self.save()

            elif command.startswith("save"):
                self.save()

            elif command.startswith("close"):
                self.close()
                sys.exit(0)

            elif command.startswith("add-site"):
                site = command[len("add-site"):]
                if not site.strip():
                    print("You must specify a site!")
                    continue
                if self.fetch(site):
                    print("Site already exists in the database!")
                    continue
                details = []
                for i, detail in enumerate(["Link: ", "Email: ", "Phone: ", "Username: ", "Password: "]):
                    user_input = input(detail)
                    if not user_input:
                        details.append("None")
                    else:
                        details.append(user_input)
                confirm = input("Confirm: Y/N")
                if confirm.strip().lower() == "y":
                    self.add(*details)
                    self.save()
                    print("Successfully updated the database!")
                else:
                    continue

            elif command.startswith("login-with"):
                site = command[len("login-with"):]
                if not site.strip():
                    print("You must specify a site!")
                    continue

                self.login_with(site)

            elif command.startswith("show-table"):
                self.show_table()

            elif command.startswith("fetch"):
                site = command[len("fetch"):]
                if not site.strip():
                    print("You must specify a site!")
                    continue

                data = self.fetch(site)
                if data:
                    print(f"Data for {site}:", *data)

                else:
                    print(f"No data found for site: {site}")


class TableWindow(QDialog):

    def __init__(self, headers, data):
        super().__init__()
        self.headers = headers
        self.data = data

        self.width, self.height = 602, 600

        self.setWindowTitle("Password Manager")
        self.setGeometry(500, 300, self.width, self.height)
        
        self.initUI()
        self.show()

    def initUI(self):
        self.table = QTableWidget(5, len(self.headers), self)
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.resize(self.width, self.height)
        self.table.verticalHeader().setVisible(False)
        self.table.setRowCount(len(self.data))
        for i in range(len(self.headers)):
            self.table.setColumnWidth(i, self.width // len(self.headers))

        for i, row in enumerate(self.data):
            for j, col in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(col))


"""
manager = Connection(input("Enter master password: "), input("Enter encryption key: "))
manager.commands()
"""

if __name__ == "__main__":
    password = Connection.generate_password(length=256)
    print(password)