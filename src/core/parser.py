class SQLParser:
    def __init__(self, cursor, database):
        self.cursor = cursor
        self.database = database

    def get_foreign_keys(self, table_name):
        """Get foreign key relationships for table"""
        self.cursor.execute(f"""
            SELECT 
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME,
                CONSTRAINT_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = '{self.database}'
                AND TABLE_NAME = '{table_name}'
                AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        return {row[0]: row for row in self.cursor.fetchall()}

    def get_table_comment(self, table_name):
        """Get table comment"""
        self.cursor.execute(f"""
            SELECT TABLE_COMMENT 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = '{self.database}' 
            AND TABLE_NAME = '{table_name}'
        """)
        return self.cursor.fetchone()[0]