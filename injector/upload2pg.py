import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
import json
import os
import sys
import logging
import time

def connect_with_retry(config, retries=5, delay=5):
    """Establish a connection to the PostgreSQL database with retries."""
    for i in range(retries):
        conn = connect(config)
        if conn:
            return conn
        logging.error(f"Attempt {i+1} of {retries} failed. Retrying in {delay} seconds...")
        time.sleep(delay)
    logging.error(f"All {retries} connection attempts failed.")
    return None

def connect(config):
    try:
        conn = psycopg2.connect(
            dbname=config['db'],
            user=config['username'],
            password=config['password'],
            host=config['host'],
            port=config['port']
        )
        return conn
    except psycopg2.Error as e:
        logging.error(f"Connection to database failed: {e}")
        return None

def disconnect(conn):
    if conn:
        try:
            conn.close()
            logging.info("Database connection closed.")
        except Exception as e:
            logging.error(f"Failed to close the connection: {e}")

def create_db(config):
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=config['username'],
            password=config['password'],
            host=config['host'],
            port=config['port']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(
            sql.SQL("SELECT 1 FROM pg_catalog.pg_database WHERE datname = {}")
            .format(sql.Literal(config['db']))
        )
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(config['db']))
            )
            logging.info(f"Database '{config['db']}' created successfully.")
            return True
        else:
            logging.info(f"Database '{config['db']}' already exists.")
            return True

    except psycopg2.Error as e:
        logging.error(f"Database creation check failed: {e}")
        return False

def initialize_tables(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actors (
                id BIGINT PRIMARY KEY,
                login TEXT,
                display_login TEXT,
                url TEXT,
                avatar_url TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repos (
                id BIGINT PRIMARY KEY,
                name TEXT,
                url TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orgs (
                id BIGINT PRIMARY KEY,
                login TEXT,
                url TEXT,
                avatar_url TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id BIGINT PRIMARY KEY,
                type TEXT,
                actor_id BIGINT REFERENCES actors(id),
                repo_id BIGINT REFERENCES repos(id),
                payload TEXT,
                public BOOLEAN,
                created_at DATE,
                updated_at DATE,
                org_id BIGINT REFERENCES orgs(id)
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eventconfig (
                start_date DATE,
                end_date DATE,
                users TEXT[],
                projects TEXT[],
                mode TEXT
            );
        """)
        conn.commit()
    except psycopg2.Error as e:
        logging.error(f"Table creation failed: {e}")

def insert_eventconfig(conn, config):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM eventconfig")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute("""
                INSERT INTO eventconfig (start_date, end_date, users, projects, mode)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                datetime.strptime(config['start_date'], '%Y-%m-%d').date(),
                datetime.strptime(config['end_date'], '%Y-%m-%d').date(),
                config['users'],
                config['projects'],
                config['mode']
            ))
        else:
            cursor.execute("""
                UPDATE eventconfig
                SET start_date = %s,
                    end_date = %s,
                    users = %s,
                    projects = %s,
                    mode = %s
            """, (
                datetime.strptime(config['start_date'], '%Y-%m-%d').date(),
                datetime.strptime(config['end_date'], '%Y-%m-%d').date(),
                config['users'],
                config['projects'],
                config['mode']
            ))
        conn.commit()
    except psycopg2.Error as e:
        logging.error(f"Failed to insert or update eventconfig: {e}")
        conn.rollback()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        conn.rollback()

def insert_event_if_not_exist(conn, event):
    try:
        cursor = conn.cursor()
        conn.autocommit = False
        
        # Insert actor
        cursor.execute("""
            INSERT INTO actors (id, login, display_login, url, avatar_url)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            event['actor'].get('id'),
            event['actor'].get('login'),
            event['actor'].get('display_login'),
            event['actor'].get('url'),
            event['actor'].get('avatar_url')
        ))

        # Insert repo
        cursor.execute("""
            INSERT INTO repos (id, name, url)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            event['repo'].get('id'),
            event['repo'].get('name'),
            event['repo'].get('url')
        ))

        # Insert org if exists
        if 'org' in event:
            cursor.execute("""
                INSERT INTO orgs (id, login, url, avatar_url)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                event['org'].get('id'),
                event['org'].get('login'),
                event['org'].get('url'),
                event['org'].get('avatar_url')
            ))

        # Insert event
        cursor.execute("""
            INSERT INTO events (id, type, actor_id, repo_id, payload, public, created_at, updated_at, org_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            event.get('id'),
            event.get('type'),
            event['actor'].get('id'),
            event['repo'].get('id'),
            json.dumps(event.get('payload', {})),
            event.get('public'),
            datetime.strptime(event.get('created_at', '1970-01-01T00:00:00Z'), '%Y-%m-%dT%H:%M:%SZ'),
            datetime.now(),
            event['org'].get('id') if 'org' in event else None
        ))

        conn.commit()
    except psycopg2.Error as e:
        logging.error(f"An error occurred during database operation: {e}")
        conn.rollback()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.autocommit = True
