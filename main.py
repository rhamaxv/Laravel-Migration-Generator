import argparse
import json
import os
from config import main

def create_config(args):
    config = {
        "user": args.user,
        "password": args.password,
        "host": args.host,
        "port": args.port,
        "database": args.database,
        "templates": {
            "migration": args.migration_template,
            "foreign_key": args.foreign_key_template
        },
        "exclude_tables": args.exclude_tables.split(',') if args.exclude_tables else [],
        "only_include_tables": args.only_include_tables.split(',') if args.only_include_tables else []
    }
    
    with open(args.config, 'w') as f:
        json.dump(config, f, indent=4)
    
    return config

def parse_args():
    parser = argparse.ArgumentParser(description='Laravel Migration Generator')
    
    parser.add_argument('-c', '--config', 
                       default='config.json',
                       help='Path to config file (default: config.json)')
    
    parser.add_argument('-u', '--user',
                       help='Database user')
    parser.add_argument('-p', '--password',
                       help='Database password')
    parser.add_argument('-H', '--host',
                       default='127.0.0.1',
                       help='Database host (default: 127.0.0.1)')
    parser.add_argument('-P', '--port',
                       type=int,
                       default=3306,
                       help='Database port (default: 3306)')
    parser.add_argument('-d', '--database',
                       help='Database name')
    parser.add_argument('-mt', '--migration-template',
                       default='templates/migration.txt',
                       help='Path to migration template (default: templates/migration.txt)')
    parser.add_argument('-ft', '--foreign-key-template',
                       default='templates/foreign_key.txt',
                       help='Path to foreign key template (default: templates/foreign_key.txt)')
    parser.add_argument('-e', '--exclude-tables',
                       help='Comma-separated list of tables to exclude')
    parser.add_argument('-i', '--only-include-tables',
                       help='Comma-separated list of tables to include')
    parser.add_argument('-s', '--save-config',
                       action='store_true',
                       help='Save provided arguments to config file')
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    if args.save_config or not os.path.exists(args.config):
        if not all([args.user, args.password, args.database]):
            print("Error: When creating a new config, you must provide user, password, and database")
            exit(1)
        create_config(args)
    
    main()
    