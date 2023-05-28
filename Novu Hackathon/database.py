import sqlite3
from sqlite3 import Error

DB_FILE = 'notification_system.db'


class DatabaseManager:
    def __init__(self):
        self.conn = self.create_connection()

    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            print(f'Successfully connected to the database: {DB_FILE}')
        except Error as e:
            print(e)
        return conn

    def create_tables(self):
        try:
            c = self.conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS Vehicle (
                    vin TEXT PRIMARY KEY,
                    make TEXT NOT NULL,
                    model TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    mileage INTEGER NOT NULL,
                    owner_email TEXT NOT NULL,
                    owner_phone_number TEXT NOT NULL
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS MaintenanceJob (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service TEXT NOT NULL,
                    interval INTEGER NOT NULL,
                    last_date DATE NOT NULL,
                    vin TEXT,
                    FOREIGN KEY (vin) REFERENCES Vehicle (vin)
                )
            ''')
            print('Tables created successfully.')
        except Error as e:
            print(e)

    def close_connection(self):
        if self.conn:
            self.conn.close()


class Vehicle:
    def __init__(self, vin, make, model, year, mileage, owner_email, owner_phone_number):
        self.vin = vin
        self.make = make
        self.model = model
        self.year = year
        self.mileage = mileage
        self.owner_email = owner_email
        self.owner_phone_number = owner_phone_number


class MaintenanceJob:
    def __init__(self, service, interval, last_date, vin):
        self.service = service
        self.interval = interval
        self.last_date = last_date
        self.vin = vin
