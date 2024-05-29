import re

VALID_FUNCTIONS = [
    'avg', 'count', 'max', 'min', 'sum', 'abs', 'ceil', 'floor', 'round', 'mod',
    'current_date', 'current_time', 'current_timestamp', 'date_add', 'date_sub', 
    'datediff', 'now', 'to_date', 'to_char', 'to_timestamp', 'concat', 'length', 
    'lower', 'upper', 'substring', 'trim', 'ltrim', 'rtrim', 'replace', 'coalesce', 
    'nullif', 'case', 'if'
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

def validate_sql(query):
    query = ' '.join(query.split())
    query = query.strip()
    
    if not query.lower().startswith('select'):
        return False, "Query deve começar com SELECT"
    
    if not is_balanced_parentheses(query):
        return False, "Parênteses desbalanceados"
    
    if 'from' not in query.lower():
        return False, "Query deve conter cláusula FROM"

    pattern = r'^\s*SELECT\s+.*\s+FROM\s+.*(\s+WHERE\s+.*)?$'
    if not re.match(pattern, query, re.IGNORECASE):
        return False, "Estrutura da query inválida. A estrutura esperada é: SELECT ... FROM ... [WHERE ...]"
    
    for func in VALID_FUNCTIONS:
        pattern = rf'\b{func}\b\('
        if re.search(pattern, query, re.IGNORECASE) and not re.search(rf'{pattern}[^\)]*\)', query):
            return False, f"Função {func} utilizada de forma incorreta"

    return True, "Query SQL é válida"

if __name__ == "__main__":
    test_queries = [
        "SELECT * FROM users WHERE id = 1",
        "SELECT name, email FROM users",
        "INSERT INTO users (name, email) VALUES ('John', 'john@example.com')",
        "SELECT COUNT(*) FROM orders",
        "SELECT * FROM orders WHERE user_id = (SELECT id FROM users WHERE email = 'john@example.com')"
    ]
    for query in test_queries:
        is_valid, message = validate_sql(query)
        print(f"Query: {query}\nIs valid: {is_valid}\nMessage: {message}\n")
