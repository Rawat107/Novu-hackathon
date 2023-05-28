from database import DatabaseManager
from notification import NotificationManager

# Create database manager
db_manager = DatabaseManager()

# Create tables
db_manager.create_tables()

# Prompt for adding a vehicle
def add_vehicle_prompt():
    print("Add a new vehicle:")
    vin = input('Enter VIN: ')
    make = input('Enter make: ')
    model = input('Enter model: ')
    year = int(input('Enter year: '))
    mileage = int(input('Enter mileage: '))
    owner_email = input("Enter owner's email address: ")
    owner_phone = input("Enter owner's phone number: ")

    # Add the vehicle to the database
    db_manager.add_vehicle(vin, make, model, year, mileage, owner_email, owner_phone)

# Prompt for adding a maintenance job
def add_maintenance_job_prompt():
    print("Add a new maintenance job:")
    service = input('Enter service: ')
    interval = int(input('Enter interval (in days): '))
    last_date = input('Enter last date (YYYY-MM-DD): ')
    vin = input('Enter VIN: ')

    # Add the maintenance job to the database
    db_manager.add_maintenance_job(service, interval, last_date, vin)

# Prompt for actions
def prompt_actions():
    while True:
        print("\nSelect an action:")
        print("1. Add a vehicle")
        print("2. Add a maintenance job")
        print("3. Schedule notifications")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")
        
        if choice == "1":
            add_vehicle_prompt()
        elif choice == "2":
            add_maintenance_job_prompt()
        elif choice == "3":
            # Schedule notifications
            NotificationManager.schedule_notifications(db_manager.conn)
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")

# Prompt for actions
prompt_actions()

# Close the database connection
db_manager.close_connection()
