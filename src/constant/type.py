FIELD_TYPE_MAPPINGS = {
    'tinyint': 'tinyInteger',
    'int': 'integer',
    'bigint unsigned': 'unsignedBigInteger',
    'bigint': 'unsignedBigInteger',
    'varchar': 'string',
    'char': 'char',
    'text': 'text',
    'mediumtext': 'mediumText',
    'longtext': 'longText',
    'json': 'json',
    'decimal': 'decimal',
    'float': 'float',
    'double': 'double',
    'boolean': 'boolean',
    'enum': 'enum',
    'date': 'date',
    'datetime': 'datetime',
    'timestamp': 'timestamp',
}

FILTER_FIELD_TYPE_PARAMS = {
    'tinyInteger': lambda _: [],
    'integer': lambda _: [],
    'bigInteger': lambda _: [],
    'increments': lambda _: [],
    'boolean': lambda _: [],
    'json': lambda _: [],
    'text': lambda _: [],
    'mediumText': lambda _: [],
    'longText': lambda _: [],
    'date': lambda _: [],
    'datetime': lambda _: [],
    'timestamp': lambda _: [],
    'decimal': lambda x: x,
    'float': lambda x: x,
    'double': lambda x: x,
    'enum': lambda x: ["'{}'".format(choice.strip("'")) for choice in x],
}

NULLABLE_FIELD_TYPES = {
    'varchar', 'char', 'text', 'mediumtext', 'longtext',
    'json', 'decimal', 'float', 'double',
    'timestamp', 'datetime', 'date', 'enum'
}