import re

VALID_FUNCTIONS = [
    'avg', 'count', 'max', 'min', 'sum', 'abs', 'ceil', 'floor', 'round', 'mod',
    'current_date', 'current_time', 'current_timestamp', 'date_add', 'date_sub', 
    'datediff', 'now', 'to_date', 'to_char', 'to_timestamp', 'concat', 'length', 
    'lower', 'upper', 'substring', 'trim', 'ltrim', 'rtrim', 'replace', 'coalesce', 
    'nullif', 'case', 'if', 'like'
]

def is_balanced_parentheses(query):
    stack = []
    for char in query:
        if char == '(':
            stack.append(char)
        elif char == ')':
            if not stack:
                return False
            stack.pop()
    return not stack

def is_balanced_quotes(query):
    single_quotes = query.count("'")
    double_quotes = query.count('"')
    return single_quotes % 2 == 0 and double_quotes % 2 == 0

def remove_comments(query): # função necessária para remover erro de linhas comentadas sendo tratadas como queries inválidas
    # remove linhas que começam com --
    query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
    # remove blocos de comentários
    query = re.sub(r'/\*[\s\S]*?\*/', '', query)
    return query.strip()

def split_queries(query):
    return re.findall(r'(?:[^;"]|"(?:\\.|[^"])*")+', query)

def validate_single_sql(query):
    query = ' '.join(query.split())
    query = query.strip()
    
    if not query:
        return True, "Query vazia"
    
    if not query.lower().startswith('select'):
        return False, "Query deve começar com SELECT"
    
    if not is_balanced_parentheses(query):
        return False, "Parênteses desbalanceados"
    
    if not is_balanced_quotes(query):
        return False, "Número de aspas desbalanceado"
    
    if 'from' not in query.lower():
        return False, "Query deve conter cláusula FROM"
    
    pattern = r'^\s*SELECT\s+.*\s+FROM\s+.*(\s+WHERE\s+.*)?$'
    if not re.match(pattern, query, re.IGNORECASE):
        return False, "Estrutura da query inválida. A estrutura esperada é: SELECT ... FROM ... [WHERE ...]"
    
    for func in VALID_FUNCTIONS:
        pattern = rf'\b{func}\b\s*\('
        if re.search(pattern, query, re.IGNORECASE):
            nested_query = re.search(rf'{pattern}.*?\)', query)
            if not nested_query:
                return False, f"Função {func} utilizada de forma incorreta"
    
    return True, "Query SQL é válida"

def validate_sql(query):
    query = remove_comments(query)
    queries = split_queries(query)
    
    results = []
    for i, single_query in enumerate(queries, 1):
        is_valid, message = validate_single_sql(single_query)
        results.append((is_valid, f"Query {i}: {message}"))
    
    all_valid = all(result[0] for result in results)
    
    if all_valid:
        return True, "Todas as queries são válidas"
    else:
        invalid_messages = [msg for valid, msg in results if not valid]
        return False, "; ".join(invalid_messages)

if __name__ == "__main__":
    test_queries = [
        "SELECT * FROM USERS\n--SELECT * FROM PESSOAS\nWHERE ID > 10\n--WHERE ID < 10",
        "SELECT name, email FROM users",
        "INSERT INTO users (name, email) VALUES ('John', 'john@example.com')",
        "SELECT COUNT(*) FROM orders",
        "SELECT * FROM orders WHERE user_id = (SELECT id FROM users WHERE email = 'john@example.com')",
        "SELECT * FROM orders WHERE description = 'Order \"Special\"'",
    ]

    for query in test_queries:
        is_valid, message = validate_sql(query)
        print(f"Query: {query}\nIs valid: {is_valid}\nMessage: {message}\n")