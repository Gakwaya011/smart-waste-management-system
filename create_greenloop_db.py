import mysql.connector
from mysql.connector import errorcode

# Database connection details
config = {
    'user': 'yourusername',  # replace with your MySQL username
    'password': 'yourpassword',  # replace with your MySQL password
    'host': '127.0.0.1',  # replace with your MySQL host if it's different
}

DB_NAME = 'greenloop'

TABLES = {}
TABLES['users'] = (
    "CREATE TABLE `users` ("
    "  `id` int NOT NULL AUTO_INCREMENT,"
    "  `username` varchar(45) NOT NULL,"
    "  `email` varchar(45) NOT NULL,"
    "  `password` varchar(45) NOT NULL,"
    "  `option` varchar(45) NOT NULL,"
    "  PRIMARY KEY (`id`),"
    "  UNIQUE KEY `username` (`username`),"
    "  UNIQUE KEY `email` (`email`)"
    ") ENGINE=InnoDB")

TABLES['bookings'] = (
    "CREATE TABLE `bookings` ("
    "  `id` int NOT NULL AUTO_INCREMENT,"
    "  `username` varchar(45) NOT NULL,"
    "  `date` date NOT NULL,"
    "  `adress` varchar(45) NOT NULL,"
    "  `email` varchar(45) NOT NULL,"
    "  `status` varchar(45) NOT NULL,"
    "  `company` varchar(45) NOT NULL,"
    "  `revenue` varchar(45) NOT NULL,"
    "  PRIMARY KEY (`id`),"
    "  UNIQUE KEY `username` (`username`)"
    ") ENGINE=InnoDB")

def create_database(cursor):
    try:
        cursor.execute(
            f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print(f"Creating table {table_name}: ", end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

try:
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    try:
        cursor.execute(f"USE {DB_NAME}")
    except mysql.connector.Error as err:
        print(f"Database {DB_NAME} does not exists.")
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print(f"Database {DB_NAME} created successfully.")
            cnx.database = DB_NAME
        else:
            print(err)
            exit(1)

    create_tables(cursor)

    cursor.close()
    cnx.close()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
