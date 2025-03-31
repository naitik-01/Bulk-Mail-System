import sqlite3
from cryptography.fernet import Fernet
import subprocess
import sys

# Function to check and install required packages
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install required dependencies if not already installed
try:
    import cryptography
except ImportError:
    print("cryptography module not found, installing...")
    install_package("cryptography")

# Generate encryption key
key = Fernet.generate_key()
cipher = Fernet(key)

# Save encryption key to a file (DO NOT SHARE THIS FILE!)
with open("key.key", "wb") as key_file:
    key_file.write(key)

# Connect to SQLite database
conn = sqlite3.connect("email_credentials.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS credentials (
        email TEXT, 
        encrypted_password BLOB
    )
''')

# Check if credentials are already stored
cursor.execute("SELECT * FROM credentials")
result = cursor.fetchone()

# If credentials do not exist, insert them
if result is None:
    email = "yourmail.com" # Replace with your mail
    app_password = "------------"  # Replace this with your NEW App Password

    # Encrypt the password
    encrypted_password = cipher.encrypt(app_password.encode())

    cursor.execute("INSERT INTO credentials (email, encrypted_password) VALUES (?, ?)", 
                   (email, encrypted_password))

    conn.commit()
    print("✅ Gmail credentials stored securely!")
else:
    print("Credentials already stored in the database.")

conn.close()
