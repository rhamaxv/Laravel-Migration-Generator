Laravel Migration Generator
==========================
The Laravel Migration Generator is a tool designed to help Laravel developers automatically generate migration files for their MySQL database schema. This tool simplifies the process of creating database migrations, including foreign key relationships, saving you time and effort. It's especially useful for large projects or when you need to quickly regenerate migrations.

## It's especially useful for:
- Large projects with complex database structures.
- Migrating legacy databases into Laravel applications.
- Quickly regenerating migrations after schema changes.

## Features:
- **Automatic Migration File Generation**: Generate Laravel migration files based on your MySQL database schema.
- **Foreign Key Handling**: Automatically create separate migration files for foreign key relationships.
- **Customizable Templates**: Use your own templates for migrations and foreign keys.
- **Selective Table Inclusion/Exclusion**: Process specific tables or exclude unnecessary ones.
- **Ordered Output**: Ensures migrations are ordered based on table dependencies to avoid foreign key conflicts.


Quick Start:
-----------

1. Install requirements:
```python
pip install -r requirements.txt
```

2. Run with config file:
```python
python main.py
```

3. Or run with command line:
```python
python main.py -u root -p your_password -d your_database --save-config
```
Available Options:
----------------
| Option                | Description                                | Default              |
|-----------------------|--------------------------------------------|----------------------|
| `-c`, `--config`      | Config file path                          | `config.json`        |
| `-u`, `--user`        | Database user                             |                      |
| `-p`, `--password`    | Database password                         |                      |
| `-H`, `--host`        | Database host                             | `127.0.0.1`         |
| `-P`, `--port`        | Database port                             | `3306`              |
| `-d`, `--database`    | Database name                             |                      |
| `-mt`, `--migration-template` | Migration template path           |                      |
| `-ft`, `--foreign-key-template` | Foreign key template path       |                      |
| `-e`, `--exclude-tables` | Comma-separated tables to exclude       |                      |
| `-i`, `--only-include-tables` | Comma-separated tables to include |                      |
| `-s`, `--save-config` | Save arguments to config file             |                      |


Examples:
--------
1. Basic usage:
```python
python main.py
```

2. Generate for specific database:
```python
python main.py -u root -p password123 -d my_database
```

3. Exclude tables:
```python
python main.py -u root -p password123 -d my_database -e migrations,logs,cache
```

4. Include only specific tables:
```python
python main.py -u root -p password123 -d my_database -i users,posts,comments
```

5. Custom templates:
```python
python main.py -u root -p password123 -d my_database -mt custom/migration.txt -ft custom/foreign_key.txt
```

Supported MySQL Data Types:
-------------------------
- Numeric: TINYINT, SMALLINT, MEDIUMINT, INT, BIGINT, DECIMAL, FLOAT, DOUBLE
- String: CHAR, VARCHAR, TEXT, LONGTEXT, ENUM, SET
- Date/Time: DATE, DATETIME, TIMESTAMP, TIME, YEAR
- Spatial: GEOMETRY, POINT, LINESTRING, POLYGON, MULTIPOINT
- Others: JSON, BLOB

Notes:
------
- Foreign key migrations are generated separately
- Tables are ordered based on relationships
- Comments and metadata are preserved
