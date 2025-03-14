from ..constant.type import *
from ..utils import *
from ..utils.file import *
from ..utils.sql import *
from .parser import SQLParser
from .field_generator import FieldGenerator
from .foreign_key_generator import ForeignKeyGenerator
import os
from tqdm import tqdm
from ..utils.log import info_logger, error_logger

class MigrationGenerator:
    def __init__(self, config):
        self.config = config
        self.template = load_template(config.get('templates', {}).get('migration'))
        self.foreign_key_template = load_template(config.get('templates', {}).get('foreign_key'))
        self.foreign_key_constraints = {}
        self.field_generator = FieldGenerator()
        self.fk_generator = ForeignKeyGenerator()
        
    def generate_migrations(self, cursor, database):
        folder, datetime_prefix = create_output_folder(database)
        sql_parser = SQLParser(cursor, database)
        
        cursor.execute(f"SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA = '{database}';")
        table_names = [row[0] for row in cursor]
        
        if self.config.get('only_include_tables'):
            table_names = [t for t in table_names if t in self.config['only_include_tables']]
        else:
            table_names = [t for t in table_names if t not in self.config.get('exclude_tables', [])]
            
        with tqdm(total=len(table_names), desc="Generating migrations", 
                 bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}',
                 dynamic_ncols=True, position=0, leave=True) as pbar:
            
            for table_name in table_names:
                try:
                    self._generate_table_migration(cursor, sql_parser, table_name, folder, datetime_prefix, include_fk=False)
                    info_logger.info(f"Successfully processed table: {table_name}")
                except Exception as e:
                    error_logger.error(f"Failed: {table_name} - {str(e)}")
                finally:
                    pbar.update(1)
        
        
        if self.foreign_key_constraints:
            self._generate_foreign_key_migrations(cursor, folder, datetime_prefix)

        
        sort_migration_files(folder)

    def _generate_table_migration(self, cursor, sql_parser, table_name, folder, timestamp_prefix, include_fk=False, pbar=None):
        try:
            info_logger.info(f"Generating migration for table: {table_name}")
            
            cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
            create_table_sql = cursor.fetchone()[1]
            
            foreign_keys = sql_parser.get_foreign_keys(table_name)
            
            if not include_fk and foreign_keys:
                self.foreign_key_constraints[table_name] = foreign_keys
                foreign_keys = {}
            
            formatted_sql = "     * " + create_table_sql.replace("\n", "\n     * ")
            
            table_comment = sql_parser.get_table_comment(table_name)
            table_comment_code = f"\n        DB::statement(\"ALTER TABLE `{table_name}` comment '{table_comment}'\");" if table_comment else ''

            cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")
            columns = cursor.fetchall()

            table_schema_codes = []
            for row in columns:
                field, field_type, collation, null, key, default, extra, privileges, comment = row

                if field in self.config.get('exclude_fields', []):
                    continue

                field_type_split = field_type.split('(')
                base_type = field_type_split[0].lower()
                field_type_name = FIELD_TYPE_MAPPINGS.get(base_type, base_type)

                if base_type == 'enum':
                    enum_str = field_type.split('(')[1].rstrip(')')
                    enum_values = [val.strip("'") for val in enum_str.split(',')]
                    enum_array = "['" + "', '".join(val.strip() for val in enum_values) + "']"
                    field_type_params = [f"'{field}'", enum_array]
                    field_type_name = 'enum'
                elif extra == 'auto_increment' and field == 'id':
                    field_type_name = 'id'
                    field_type_params = []
                else:
                    field_type_params = [f"'{field}'"]
                    
                    if len(field_type_split) > 1:
                        params_str = field_type_split[1].split(')')[0]
                        if params_str:
                            params = params_str.split(',')
                            if field_type_name in ['decimal', 'double', 'float']:
                                field_type_params.extend(params)
                            elif field_type_name == 'string':
                                field_type_params.append(params[0])

                appends = []
                if null == 'YES':
                    appends.append('->nullable()')
                if default is not None:
                    if default == 'CURRENT_TIMESTAMP':
                        appends.append("->default(DB::raw('CURRENT_TIMESTAMP'))")
                    elif field_type_name in ['boolean', 'tinyInteger', 'integer', 'bigInteger', 'unsignedBigInteger']:
                        appends.append(f"->default({default})")
                    else:
                        appends.append(f"->default('{default}')")
                if comment:
                    escaped_comment = comment.replace("'", "\\'")
                    appends.append("->comment('{}')".format(escaped_comment))
                if key == 'UNI':
                    appends.append('->unique()')
                if key == 'MUL' and field not in foreign_keys:
                    appends.append('->index()')

                params_str = f"({', '.join(field_type_params)})" if field_type_params else "()"
                table_schema_code = f"$table->{field_type_name}{params_str}{''.join(appends)};"
                table_schema_codes.append(f"            {table_schema_code}")

            for field, fk in foreign_keys.items():
                ref_table = fk[1]
                ref_field = fk[2]
                table_schema_codes.append(
                    f"            // Depends on: {ref_table}\n"
                    f"            $table->foreign('{field}')->references('{ref_field}')"
                    f"->on('{ref_table}')->onDelete('cascade')->onUpdate('cascade');"
                )

            classname = ''.join(x.capitalize() for x in table_name.split('_'))
            if not classname.endswith('Table'):
                classname += 'Table'

            field_defs = []
            for field_def in self.field_generator.get_field_definitions(cursor, table_name):
                field_defs.append(f"            {field_def}")
                if pbar:
                    pbar.set_postfix_str(f"Processing: {table_name}")
            

            up_code = [
                f"Schema::create('{table_name}', function (Blueprint $table) {{",
                *field_defs,
                "});"
            ]
            
            down_code = [f"Schema::dropIfExists('{table_name}');"]
            

            replacements = {
                '{{classname}}': classname,
                '{{create_table_sql}}': sql_parser.get_table_comment(table_name),
                '{{schema_codes}}': '\n'.join(up_code),
                '{{drop_codes}}': '\n'.join(down_code)
            }

            migration_code = self.template
            for key, value in replacements.items():
                migration_code = migration_code.replace(key, value)

            filename = f"{timestamp_prefix}_create_{table_name}_table.php"
            filepath = os.path.join(folder, filename)
            with open(filepath, 'w') as f:
                f.write(migration_code)

            info_logger.info(f"Successfully generated migration for table: {table_name}")
            return replacements
            
        except Exception as e:
            error_logger.error(f"Error generating migration for {table_name}: {str(e)}")
            raise

    def _generate_foreign_key_migrations(self, cursor, folder, datetime_prefix):
        return self.fk_generator.generate(
            cursor, 
            folder, 
            datetime_prefix, 
            self.foreign_key_constraints,
            self.foreign_key_template
        )