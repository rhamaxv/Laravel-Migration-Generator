import os
import datetime
from ..utils.log import info_logger, error_logger

class ForeignKeyGenerator:
    def generate(self, cursor, folder, datetime_prefix, foreign_key_constraints, template):
        try:
            if not foreign_key_constraints:
                info_logger.info("No foreign key constraints to generate")
                return
                
            info_logger.info(f"Generating foreign key constraints for {len(foreign_key_constraints)} tables")
            classname = 'AddForeignKeyConstraints'
            schema_codes, drop_codes = self._generate_constraint_codes(cursor, foreign_key_constraints)
            
            if not schema_codes:
                info_logger.info("No valid foreign key constraints found")
                return
                
            migration_code = self._generate_migration_code(
                template, 
                classname, 
                schema_codes, 
                drop_codes
            )
            
            self._write_migration_file(
                folder,
                datetime_prefix,
                migration_code,
                len(foreign_key_constraints)
            )
            info_logger.info("Successfully generated foreign key constraints migration")
            
        except Exception as e:
            error_logger.error(f"Error generating foreign key constraints: {str(e)}")
            raise

    def _generate_constraint_codes(self, cursor, foreign_key_constraints):
        try:
            info_logger.info("Generating constraint codes")
            table_columns = self._get_table_columns(cursor, foreign_key_constraints.keys())
            schema_codes = []
            drop_codes = []
            
            for table_name, foreign_keys in foreign_key_constraints.items():
                info_logger.debug(f"Processing constraints for table: {table_name}")
                codes = self._process_table_constraints(
                    cursor, 
                    table_name, 
                    foreign_keys, 
                    table_columns
                )
                if codes:
                    schema_codes.extend(codes[0])
                    drop_codes.extend(codes[1])
                    
            info_logger.info(f"Generated {len(schema_codes)} constraint codes")
            return schema_codes, drop_codes
            
        except Exception as e:
            error_logger.error(f"Error generating constraint codes: {str(e)}")
            raise

    def _process_table_constraints(self, cursor, table_name, foreign_keys, table_columns):
        try:
            info_logger.debug(f"Processing constraints for table: {table_name}")
            temp_schema_codes = [f"Schema::table('{table_name}', function (Blueprint $table) {{"]
            temp_drop_codes = [f"Schema::table('{table_name}', function (Blueprint $table) {{"]
            valid_fks = False

            for field, fk in foreign_keys.items():
                ref_table = fk[1]
                ref_field = fk[2]

                if ref_table not in table_columns:
                    cursor.execute(f"SHOW COLUMNS FROM `{ref_table}`")
                    table_columns[ref_table] = {row[0]: row[1].lower() for row in cursor.fetchall()}

                source_type = table_columns[table_name].get(field)
                ref_type = table_columns[ref_table].get(ref_field)

                if source_type and ref_type and self._are_types_compatible(source_type, ref_type):
                    valid_fks = True
                    temp_schema_codes.append(
                        f"            $table->foreign('{field}')->references('{ref_field}')"
                        f"->on('{ref_table}')->onDelete('cascade')->onUpdate('cascade');"
                    )
                    temp_drop_codes.append(f"            $table->dropForeign(['{field}']);")

            if valid_fks:
                temp_schema_codes.append("        });")
                temp_drop_codes.append("        });")
                return temp_schema_codes, temp_drop_codes
            return None

        except Exception as e:
            error_logger.error(f"Error processing table constraints for {table_name}: {str(e)}")
            raise

    def _get_table_columns(self, cursor, table_names):
        try:
            table_columns = {}
            for table_name in table_names:
                info_logger.debug(f"Fetching columns for table: {table_name}")
                cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
                table_columns[table_name] = {row[0]: row[1].lower() for row in cursor.fetchall()}
            return table_columns
            
        except Exception as e:
            error_logger.error(f"Error getting table columns: {str(e)}")
            raise

    def _are_types_compatible(self, source_type, ref_type):
        try:
            source_type = source_type.lower()
            ref_type = ref_type.lower()
            
            source_base = source_type.split('(')[0]
            ref_base = ref_type.split('(')[0]
            
            compatible_types = {
                'int': ['int', 'bigint', 'integer'],
                'integer': ['int', 'bigint', 'integer'],
                'bigint': ['int', 'bigint', 'integer'],
                'unsignedbigint': ['int', 'bigint', 'integer', 'unsignedbigint']
            }
            
            if source_base == ref_base:
                return True
                
            if source_base in compatible_types and ref_base in compatible_types[source_base]:
                return True
                
            return False
            
        except Exception as e:
            error_logger.error(f"Error checking type compatibility: {str(e)}")
            raise

    def _generate_migration_code(self, template, classname, schema_codes, drop_codes):
        try:
            replacements = {
                '{{classname}}': classname,
                '{{schema_codes}}': '\n'.join(schema_codes),
                '{{drop_foreign_keys}}': '\n'.join(drop_codes)
            }

            migration_code = template
            for key, value in replacements.items():
                migration_code = migration_code.replace(key, value)
                
            return migration_code
            
        except Exception as e:
            error_logger.error(f"Error generating migration code: {str(e)}")
            raise

    def _write_migration_file(self, folder, datetime_prefix, migration_code, constraint_count):
        try:
            fk_datetime = datetime.datetime.strptime(datetime_prefix, '%Y_%m_%d_%H%M%S')
            fk_datetime += datetime.timedelta(seconds=constraint_count + 1)
            fk_datetime += datetime.timedelta(seconds=1000)

            fk_datetime_prefix = fk_datetime.strftime('%Y_%m_%d_%H%M%S')
            filename = f"{fk_datetime_prefix}_add_foreign_key_constraints.php"
            filepath = os.path.join(folder, filename)
            
            with open(filepath, 'w') as f:
                f.write(migration_code)
                
            info_logger.info(f"Successfully wrote migration file: {filename}")
            
        except Exception as e:
            error_logger.error(f"Error writing migration file: {str(e)}")
            raise 