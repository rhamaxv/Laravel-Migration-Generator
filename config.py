import json
import sys
import mysql.connector
from src.core.migration_generator import MigrationGenerator

def main():
    config_file = 'config.json' if len(sys.argv) < 2 else sys.argv[1]
    try:
        with open(config_file) as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON configuration file: {e}")
        sys.exit(1)

    try:
        cnx = mysql.connector.connect(
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config.get('port', 3306),
            database=config['database']
        )
        cursor = cnx.cursor()

        generator = MigrationGenerator(config)
        generator.generate_migrations(cursor, config['database'])

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        sys.exit(1)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'cnx' in locals():
            cnx.close()