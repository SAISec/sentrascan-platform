"""
Database operations with SQL injection vulnerabilities
WARNING: This code contains intentional security vulnerabilities for testing purposes only.
"""

import sqlite3
import psycopg2

# ============================================================================
# SQL INJECTION VULNERABILITIES
# ============================================================================

def get_user_by_email(email):
    """SQL Injection - String concatenation"""
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    # VULNERABLE: Direct string interpolation
    query = "SELECT * FROM users WHERE email = '" + email + "'"
    cursor.execute(query)
    return cursor.fetchone()

def update_user_profile(user_id, bio):
    """SQL Injection - Format string"""
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    # VULNERABLE: String formatting
    query = "UPDATE users SET bio = '{}' WHERE id = {}".format(bio, user_id)
    cursor.execute(query)
    conn.commit()

def search_products(keyword):
    """SQL Injection - % operator"""
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    # VULNERABLE: % formatting
    query = "SELECT * FROM products WHERE name LIKE '%%%s%%'" % keyword
    cursor.execute(query)
    return cursor.fetchall()

def delete_order(order_id):
    """SQL Injection - f-string"""
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    # VULNERABLE: f-string with user input
    query = f"DELETE FROM orders WHERE id = {order_id}"
    cursor.execute(query)
    conn.commit()

# PostgreSQL examples
def get_postgres_user(username):
    """SQL Injection - PostgreSQL"""
    conn = psycopg2.connect("dbname=test user=test")
    cursor = conn.cursor()
    # VULNERABLE: String interpolation
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()

# ============================================================================
# HARDCODED DATABASE CREDENTIALS
# ============================================================================

DB_HOST = "localhost"
DB_USER = "admin"
DB_PASSWORD = "SuperSecretDBPassword123!"
DB_NAME = "production_db"

def get_db_connection():
    """Hardcoded database credentials"""
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

