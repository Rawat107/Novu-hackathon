import sqlite3
from sqlite3 import Error
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from twilio.rest import Client
import twilio_config
import smtp_config

DB_FILE = 'notification_system.db'

# Table creation SQL statement
CREATE_TABLE_VEHICLE = '''
CREATE TABLE IF NOT EXISTS Vehicle (
    vin TEXT PRIMARY KEY,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    mileage INTEGER NOT NULL,
    owner_email TEXT NOT NULL,
    owner_phone_number TEXT NOT NULL
);
'''

CREATE_TABLE_MAINTENANCE_JOB = '''
CREATE TABLE IF NOT EXISTS MaintenanceJob (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service TEXT NOT NULL,
    interval INTEGER NOT NULL,
    last_date DATE NOT NULL,
    vin TEXT,
    FOREIGN KEY (vin) REFERENCES Vehicle (vin)
);
'''

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        print(f'Successfully connected to the database: {DB_FILE}')
    except Error as e:
        print(e)
    return conn

def create_tables(conn):
    try:
        c = conn.cursor()
        c.execute(CREATE_TABLE_VEHICLE)
        c.execute(CREATE_TABLE_MAINTENANCE_JOB)
        print('Tables created successfully.')
    except Error as e:
        print(e)
    
def send_email_notification(service, next_service_date, owner_email):
    #email config
    sender_email = smtp_config.SENDER_EMAIL 
    sender_passward = smtp_config.SENDER_PASSWORD 
    smtp_server =smtp_config.SMTP_SERVER 
    smtp_port = smtp_config.SMTP_PORT 

    #email connect
    subject = f'{service} Maintenance Reminder'
    message = f'Dear vehicle owner,\n\nThis is a reminder that your {service} is due on {next_service_date}.\n\nPlease schedule an appointment for maintenance.\n\nBest regards,\nYour Automotive Maintenance System'

    #Contruct the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = owner_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    #Connect to the SMTP server
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_passward)
            server.send_message(msg)
        print(f'Email notification sent to {owner_email} for {service} maintenance.')
    except Exception as e:
        print(f'Failed to send email notification: {str(e)}')

def send_sms_notification(service, next_service_date, owner_phone_number):
    #sms config
    account_sid = twilio_config.TWILIO_ACCOUNT_SID
    auth_token = twilio_config.TWILIO_AUTH_TOKEN
    twilio_phone_number = twilio_config.TWILIO_PHONE_NUMBER

    #twilio client
    client = Client(account_sid, auth_token)

    #compose the SMS message
    message = f'Dear vehicle owner, this is a reminder that your {service} is due on {next_service_date}. Please schedule an appointment for maintenance'

    try:
        #send the sms notification
        client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=owner_phone_number
        )
        print(f' SMS notification sent to {owner_phone_number} for {service} maintenance')
    except Exception as e:
        print(f'Failed to send SMS notifiaciton: {str(e)}')


# def send_notification(service, next_service_date, owner_email):
    # print(f"Notification: {service} is due on {next_service_date} for vehicle owner {owner_email}")

def schedule_notifications(conn):
    try:
        c = conn.cursor()
        c.execute('''
            SELECT MaintenanceJob.vin, service, interval, last_date, owner_email, owner_phone_number
            FROM MaintenanceJob
            INNER JOIN Vehicle ON MaintenanceJob.vin = Vehicle.vin
        ''')

        rows = c.fetchall()
        for row in rows:
            vin, service, interval, last_date, owner_email, owner_phone_number = row
            #calculating the last date 
            if last_date:
                last_date = datetime.strptime(last_date, '%Y-%m-%d').date()
                next_service_date = last_date + timedelta(days=interval)
            else:
                next_service_date = datetime.now().date() + timedelta(days=interval)

            #checking if the service is due
            current_date = datetime.now().date()
            if next_service_date <= current_date:
                #send email
                send_email_notification(service, next_service_date, owner_email)
                #send sms 
                send_sms_notification(service, next_service_date, owner_phone_number)

            #updating the last date
            next_service_date_str = next_service_date.strftime('%Y-%m-%d')
            c.execute('''
                UPDATE MaintenanceJob
                SET last_date = ?
                WHERE vin = ? AND service = ?
            ''', (next_service_date_str, vin, service))
            conn.commit()    
            
        print('Notification scheduled succesfully.')

    except Error as e:
        print(e)

def add_vehicle(args):
    conn = create_connection()
    if conn is None:
        return
    
    try:
        c = conn.cursor()
        vin = input('Eneter VIN: ')
        make = input('Enter make: ')
        model = input('Enter model: ')
        year = input('Enter year: ')
        mileage = input('Enter mileage: ')
        owner_email = input('Enter owner\'s email address: ')
        owner_phone_number = input('Enter owner\'s phone number: ')
        c.execute('INSERT INTO Vehicle (vin, make, model, year, mileage, owner_email, owner_phone_number) VALUES (?,?,?,?,?,?,?)',
                (vin, make, model, year, mileage, owner_email, owner_phone_number))
        conn.commit()

        print('Vehicle added successfully.')
    except Error as e:
        print(e)
    finally:
        conn.close()

def add_maintenance_job(args):
    conn = create_connection()
    if conn is None:
        return
    
    try:
        c = conn.cursor()
        service = input('Enter service: ')
        interval = int(input('Enter interval (in days): '))
        last_date = input('Enter last date (YYYY-MM-DD): ')
        vin = input('Enter VIN: ')

        c.execute('INSERT INTO MaintenanceJob (service, interval, last_date, vin) VALUES (?, ?, ?, ?)',
                   (service, interval, last_date, vin))
        conn.commit()


        print('Maintenance job added successfully')
    except Error as e:
        print(e)
    finally:
        conn.close()


def list_vehicles(args):
    conn = create_connection()
    if conn is None:
        return
    try:
        c = conn.cursor()
        c.execute('SELECT * FROM Vehicle')
        rows = c.fetchall()
        for row in rows:
            print('VIN: ', row[0])
            print('Make: ', row[1])
            print('Model: ', row[2])
            print('Year: ', row[3])
            print('Mileage: ', row[4])
            print('Owner email: ', row[5])
            print('------------------------')

        print('Vehicle list retrived successfully. ')
    except Error as e:
        print(e)
    finally:
        conn.close()
        
def list_maintenance_jobs(args):
    conn = create_connection()
    if conn is None:
        return
    try:
        c = conn.cursor()
        c.execute('SELECT * FROM MaintenanceJob')
        rows = c.fetchall()
        for row in rows:
            print('ID: ', row[0])
            print('Service: ', row[1])
            print('Interval: ', row[2])
            print('Last date: ', row[3])
            print('VIN: ', row[4])
            print('------------------------')
        print('Maintenance job list retrived successfully. ')
    except Error as e:
        print(e)
    finally:
        conn.close()
        
def add_vehicle_parser(subparsers):
    parser = subparsers.add_parser('add-vehicle', help='Add a new vehicle')
    parser.set_defaults(func=add_vehicle)

def add_maintenance_job_parser(subparsers):
    parser = subparsers.add_parser('add-job', help='Add a new maintenance job')
    parser.set_defaults(func=add_maintenance_job)

def list_vehicles_parser(subparsers):
    parser = subparsers.add_parser('list-vehicles', help='List all vehicles')
    parser.set_defaults(func=list_vehicles)

def list_maintenance_jobs_parser(subparsers):
    parser = subparsers.add_parser('list-jobs', help='List all maintenance jobs')
    parser.set_defaults(func=list_maintenance_jobs)


def create_parser():
    parser = argparse.ArgumentParser(description='Automotive Maintenance System')

    subparsers = parser.add_subparsers()

    add_vehicle_parser(subparsers)
    add_maintenance_job_parser(subparsers)
    list_vehicles_parser(subparsers)
    list_maintenance_jobs_parser(subparsers)

    return parser


def main():
    conn = create_connection()
    if conn is None:
        return

    create_tables(conn)

    parser = create_parser()
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)

    schedule_notifications(conn)

if __name__ == '__main__':
    main()

