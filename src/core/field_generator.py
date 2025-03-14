from ..utils.log import info_logger, error_logger

class FieldGenerator:
    def get_field_definitions(self, cursor, table_name):
        """Generate Laravel migration field definitions from MySQL table"""
        try:
            info_logger.info(f"Generating field definitions for table: {table_name}")
            cursor.execute(f"""
                SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA, COLUMN_COMMENT
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """)
            
            field_defs = []
            for column in cursor.fetchall():
                name, col_type, nullable, default, extra, comment = column
                info_logger.debug(f"Processing field: {name} in table {table_name}")
                field_def = self._generate_field_definition(name, col_type, nullable, default, extra, comment)
                field_defs.append(field_def)
            
            info_logger.info(f"Successfully generated {len(field_defs)} field definitions for table: {table_name}")    
            return field_defs
            
        except Exception as e:
            error_logger.error(f"Error in get_field_definitions for {table_name}: {str(e)}")
            raise

    def _generate_field_definition(self, name, col_type, nullable, default, extra, comment):
        try:
            if name == 'id' and 'auto_increment' in extra.lower():
                return "$table->id();"
                
            field_type, length, precision = self._parse_column_type(col_type)
            field_def = self._build_field_definition(field_type, name, length, precision)
            field_def = self._add_modifiers(field_def, nullable, default, extra, comment, col_type, field_type)
            
            info_logger.debug(f"Generated field definition for: {name}")
            return field_def
            
        except Exception as e:
            error_logger.error(f"Error generating field definition for {name}: {str(e)}")
            raise

    def _parse_column_type(self, col_type):
        try:
            col_type = col_type.lower()
            length = None
            precision = None
            
            # Numeric Types
            if 'tinyint(1)' in col_type:  # Special case for boolean
                field_type = 'boolean'
            elif 'tinyint' in col_type:
                field_type = 'tinyInteger'
            elif 'smallint' in col_type:
                field_type = 'smallInteger'
            elif 'mediumint' in col_type:
                field_type = 'mediumInteger'
            elif 'int' in col_type or 'integer' in col_type:
                field_type = 'unsignedBigInteger' if 'unsigned' in col_type else 'integer'
            elif 'bigint' in col_type:
                field_type = 'unsignedBigInteger' if 'unsigned' in col_type else 'bigInteger'
            elif 'decimal' in col_type or 'numeric' in col_type:
                field_type = 'decimal'
                if '(' in col_type:
                    precision = col_type.split('(')[1].split(')')[0].split(',')
            elif 'float' in col_type:
                field_type = 'float'
                if '(' in col_type:
                    precision = col_type.split('(')[1].split(')')[0].split(',')
            elif 'double' in col_type or 'real' in col_type:
                field_type = 'double'
                if '(' in col_type:
                    precision = col_type.split('(')[1].split(')')[0].split(',')
                    
            # String Types
            elif 'char' in col_type:
                field_type = 'char'
                if '(' in col_type:
                    length = col_type.split('(')[1].split(')')[0]
            elif 'varchar' in col_type:
                field_type = 'string'
                length = col_type.split('(')[1].split(')')[0] if '(' in col_type else '255'
            elif 'tinytext' in col_type:
                field_type = 'text'  # Laravel doesn't have specific tinyText
            elif 'mediumtext' in col_type:
                field_type = 'mediumText'
            elif 'longtext' in col_type:
                field_type = 'longText'
            elif 'text' in col_type:
                field_type = 'text'
            elif 'binary' in col_type:
                field_type = 'binary'
            elif 'blob' in col_type:
                if 'tinyblob' in col_type:
                    field_type = 'binary'
                elif 'mediumblob' in col_type:
                    field_type = 'binary'
                elif 'longblob' in col_type:
                    field_type = 'binary'
                else:
                    field_type = 'binary'
            elif 'enum' in col_type:
                field_type = 'enum'
                enum_str = col_type.split('(')[1].rstrip(')')
                length = [val.strip("'").strip('"') for val in enum_str.split(',')]
            elif 'set' in col_type:
                field_type = 'set'
                set_str = col_type.split('(')[1].rstrip(')')
                length = [val.strip("'").strip('"') for val in set_str.split(',')]
                
            # Date and Time Types
            elif 'datetime' in col_type:
                field_type = 'datetime'
            elif 'timestamp' in col_type:
                field_type = 'timestamp'
            elif 'date' in col_type:
                field_type = 'date'
            elif 'time' in col_type:
                field_type = 'time'
            elif 'year' in col_type:
                field_type = 'year'
                
            # Spatial Types
            elif 'geometry' in col_type:
                field_type = 'geometry'
            elif 'point' in col_type:
                field_type = 'point'
            elif 'linestring' in col_type:
                field_type = 'lineString'
            elif 'polygon' in col_type:
                field_type = 'polygon'
            elif 'multipoint' in col_type:
                field_type = 'multiPoint'
            elif 'multilinestring' in col_type:
                field_type = 'multiLineString'
            elif 'multipolygon' in col_type:
                field_type = 'multiPolygon'
            elif 'geometrycollection' in col_type:
                field_type = 'geometryCollection'
                
            # JSON Type
            elif 'json' in col_type:
                field_type = 'json'
                
            else:
                field_type = 'string'
                length = '255'
                
            info_logger.debug(f"Parsed column type: {col_type} to {field_type}")
            return field_type, length, precision
            
        except Exception as e:
            error_logger.error(f"Error parsing column type {col_type}: {str(e)}")
            raise

    def _build_field_definition(self, field_type, name, length, precision):
        try:
            if field_type == 'enum':
                enum_values = "['" + "', '".join(length) + "']"
                field_def = f"$table->enum('{name}', {enum_values})"
            elif field_type == 'set':
                set_values = "['" + "', '".join(length) + "']"
                field_def = f"$table->set('{name}', {set_values})"
            elif field_type in ['string', 'char'] and length:
                field_def = f"$table->{field_type}('{name}', {length})"
            elif field_type in ['decimal', 'float', 'double'] and precision:
                field_def = f"$table->{field_type}('{name}', {precision[0]}, {precision[1]})"
            elif field_type in ['geometry', 'point', 'lineString', 'polygon', 
                              'multiPoint', 'multiLineString', 'multiPolygon', 
                              'geometryCollection']:
                field_def = f"$table->{field_type}('{name}')"
            else:
                field_def = f"$table->{field_type}('{name}')"
                
            info_logger.debug(f"Built base field definition for {name}: {field_def}")
            return field_def
            
        except Exception as e:
            error_logger.error(f"Error building field definition for {name}: {str(e)}")
            raise

    def _add_modifiers(self, field_def, nullable, default, extra, comment, col_type, field_type):
        try:
            if nullable == 'YES':
                field_def += "->nullable()"
                
            if default is not None:
                if default == 'CURRENT_TIMESTAMP':
                    field_def += "->default(DB::raw('CURRENT_TIMESTAMP'))"
                elif field_type in ['string', 'text']:
                    field_def += f"->default('{default}')"
                else:
                    field_def += f"->default({default})"
                    
            if 'auto_increment' in extra.lower():
                field_def += "->autoIncrement()"
                
            if comment:
                escaped_comment = comment.replace("'", "\\'")
                field_def += f"->comment('{escaped_comment}')"
                
            if 'unsigned' in col_type.lower() and field_type not in ['unsignedBigInteger']:
                field_def += "->unsigned()"
                
            field_def += ";"
            
            info_logger.debug(f"Added modifiers to field definition: {field_def}")
            return field_def
            
        except Exception as e:
            error_logger.error(f"Error adding modifiers to field definition: {str(e)}")
            raise 