import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",         # or your MySQL username
    password="Shakti@2027",  # replace with your password
    database="smartzone_r"
)

cursor = conn.cursor()
cursor.execute("SHOW TABLES;")
print("Tables:", cursor.fetchall())

conn.close()