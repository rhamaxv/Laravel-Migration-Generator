import re
import os
import datetime
import glob
from collections import defaultdict
from tqdm import tqdm
from .log import info_logger, error_logger

def format_sql(sql):
    return sql.replace('\n', '\n     * ')

def analyze_foreign_keys(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    references = re.findall(r"->on\('(\w+)'\)", content)
    table_name = re.search(r"Schema::create\('(\w+)'", content)
    
    if table_name:
        table_name = table_name.group(1)
        return table_name, references
    return None, []

def sort_migration_files(output_folder):
    migration_files = glob.glob(f"{output_folder}/*.php")
    info_logger.info(f"Starting to sort {len(migration_files)} migration files")
    
    dependencies = defaultdict(list)
    table_files = {}
    
    with tqdm(total=len(migration_files), desc="Analyzing dependencies", leave=False) as pbar:
        for file_path in migration_files:
            table_name, references = analyze_foreign_keys(file_path)
            if table_name:
                table_files[table_name] = file_path
                dependencies[table_name].extend(references)
            pbar.update(1)

    def has_cycle(node, visited, stack):
        visited[node] = True
        stack[node] = True
        
        for neighbor in dependencies[node]:
            if neighbor not in visited:
                if has_cycle(neighbor, visited, stack):
                    return True
            elif stack[neighbor]:
                return True
        
        stack[node] = False
        return False
    
    visited = {}
    stack = {}
    for node in dependencies:
        if node not in visited:
            if has_cycle(node, visited, stack):
                error_logger.error("Cycle detected in relationships!")
    
    def topological_sort():
        def get_all_referenced_tables():
            referenced = set()
            for deps in dependencies.values():
                referenced.update(deps)
            return referenced

        def ensure_referenced_tables():
            referenced = get_all_referenced_tables()
            for table in referenced:
                if table not in dependencies:
                    dependencies[table] = []

        def get_root_tables():
            all_tables = set(dependencies.keys())
            referenced = get_all_referenced_tables()
            return sorted(list(all_tables - referenced))

        def dfs(node, visited, order):
            visited[node] = True
            
            sorted_neighbors = sorted(dependencies[node])
            for neighbor in sorted_neighbors:
                if neighbor not in visited:
                    dfs(neighbor, visited, order)
            
            order.append(node)
        
        ensure_referenced_tables()
        visited = {}
        order = []
        
        root_tables = get_root_tables()
        for table in root_tables:
            if table not in visited:
                dfs(table, visited, order)
        
        remaining_tables = sorted([t for t in dependencies if t not in visited])
        for table in remaining_tables:
            if table not in visited:
                dfs(table, visited, order)
        
        info_logger.info("Dependency analysis completed")
        for table in dependencies:
            info_logger.debug(f"Table dependencies: {table} -> {dependencies[table]}")
        
        return order
    
    def validate_dependencies():
        missing_tables = set()
        for table, refs in dependencies.items():
            for ref in refs:
                if ref not in table_files:
                    missing_tables.add(ref)
        
        if missing_tables:
            error_logger.warning("Referenced tables not found:")
            for table in missing_tables:
                error_logger.warning(f"- {table}")
            error_logger.warning("Please ensure all referenced tables are created first.")

    validate_dependencies()
    ordered_tables = topological_sort()
    
    base_timestamp = datetime.datetime.now()
    interval = datetime.timedelta(seconds=1)
    
    with tqdm(total=len(ordered_tables), desc="Reordering migrations", leave=False) as pbar:
        for i, table in enumerate(ordered_tables):
            if table in table_files:
                file_path = table_files[table]
                new_timestamp = (base_timestamp + interval * i).strftime('%Y_%m_%d_%H%M%S')
                new_name = f"{new_timestamp}_create_{table}_table.php"
                new_path = os.path.join(os.path.dirname(file_path), new_name)
                
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    content = re.sub(r'(\d{4}_\d{2}_\d{2}_\d{6})', new_timestamp, content)
                    
                    with open(new_path, 'w') as f:
                        f.write(content)
                    
                    if new_path != file_path:
                        os.remove(file_path)
                    
                    info_logger.info(f"Migration ordered: {os.path.basename(file_path)} -> {new_name}")
                    info_logger.debug(f"Dependencies for {table}: {dependencies[table]}")
                except Exception as e:
                    error_logger.error(f"Error processing file {file_path}: {str(e)}")
            pbar.update(1)
    
    info_logger.info("Final migration order:")
    for i, table in enumerate(ordered_tables, 1):
        info_logger.info(f"{i}. {table}")
    
    info_logger.info(f"Successfully sorted {len(ordered_tables)} migration files.")