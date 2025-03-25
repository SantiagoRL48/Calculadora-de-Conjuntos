from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Universo fijo para el complemento
UNIVERSAL_SET = set([str(i) for i in range(1, 10)] + ['a', 'b', 'c', 'd'])

def parse_set(set_str):
    """Convierte una cadena como '1,2,a,c' en un conjunto de elementos."""
    if not set_str.strip():
        return set()
    try:
        elements = [x.strip() for x in set_str.split(',') if x.strip()]
        return set(elements)
    except Exception:
        return set()

def sorted_set_str(s, sort=True):
    """Convierte un conjunto en una cadena, opcionalmente ordenada."""
    if not s:
        return '{}'
    return '{' + ','.join(sorted(s) if sort else s) + '}'

def tokenize_expression(expr):
    """Divide una expresión en tokens, incluyendo paréntesis."""
    tokens = []
    current_token = ''
    operators = {'∪', '∩', '-', '∆', '/C', 'U', 'u', 'n'}
    parens = {'(', ')'}
    
    i = 0
    while i < len(expr):
        char = expr[i]
        if char == '/' and i + 1 < len(expr) and expr[i + 1] == 'C':
            if current_token:
                tokens.append(current_token)
                current_token = ''
            tokens.append('/C')
            i += 2
            continue
        if char in {'U', 'u'}:
            if current_token:
                tokens.append(current_token)
                current_token = ''
            tokens.append('∪')
            i += 1
            continue
        if char == 'n':
            if current_token:
                tokens.append(current_token)
                current_token = ''
            tokens.append('∩')
            i += 1
            continue
        if char in operators or char in parens or char.isspace():
            if current_token:
                tokens.append(current_token)
                current_token = ''
            if char in operators and char not in {'U', 'u', 'n'}:
                tokens.append(char)
            elif char in parens:
                tokens.append(char)
            i += 1
        else:
            current_token += char
            i += 1
    
    if current_token:
        tokens.append(current_token)
    
    tokens = [t for t in tokens if t and not t.isspace()]
    print(f"Tokens generados: {tokens}")
    return tokens

def evaluate_expression(expr, sets, sort_output):
    """Evalúa una expresión con paréntesis de manera estricta."""
    set_map = {'A': sets[0], 'B': sets[1], 'C': sets[2]}
    print(f"Set A: {sorted_set_str(sets[0])}")
    print(f"Set B: {sorted_set_str(sets[1])}")
    print(f"Set C: {sorted_set_str(sets[2])}")
    
    tokens = tokenize_expression(expr)
    if not tokens:
        return None, "Error: Expresión vacía"
    
    # Pila para operandos (conjuntos) y operadores
    operand_stack = []
    operator_stack = []
    operators = {'∪': 'union', '∩': 'intersection', '-': 'difference', '∆': 'symmetric_difference'}
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        print(f"Procesando token: {token}, Operand Stack: {[sorted_set_str(s) for s in operand_stack]}, Operator Stack: {operator_stack}")
        
        if token in set_map:
            operand_stack.append(set_map[token])
            i += 1
        elif token == '(':
            operator_stack.append(token)
            i += 1
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                op = operator_stack.pop()
                if op == '/C':
                    if not operand_stack:
                        return None, "Error: /C requiere un conjunto previo"
                    operand_stack[-1] = UNIVERSAL_SET.difference(operand_stack[-1])
                else:
                    if len(operand_stack) < 2:
                        return None, f"Error: {op} requiere dos conjuntos"
                    b = operand_stack.pop()
                    a = operand_stack.pop()
                    if operators[op] == 'union':
                        operand_stack.append(a.union(b))
                    elif operators[op] == 'intersection':
                        operand_stack.append(a.intersection(b))
                    elif operators[op] == 'difference':
                        operand_stack.append(a.difference(b))
                    elif operators[op] == 'symmetric_difference':
                        operand_stack.append(a.symmetric_difference(b))
            if operator_stack and operator_stack[-1] == '(':
                operator_stack.pop()  # Quitar el '('
            i += 1
        elif token in operators or token == '/C':
            operator_stack.append(token)
            i += 1
        else:
            return None, f"Error: Token no válido: {token}"

    # Procesar operadores restantes
    while operator_stack:
        op = operator_stack.pop()
        if op == '(':
            return None, "Error: Paréntesis no coincidentes"
        if op == '/C':
            if not operand_stack:
                return None, "Error: /C requiere un conjunto previo"
            operand_stack[-1] = UNIVERSAL_SET.difference(operand_stack[-1])
        else:
            if len(operand_stack) < 2:
                return None, f"Error: {op} requiere dos conjuntos"
            b = operand_stack.pop()
            a = operand_stack.pop()
            if operators[op] == 'union':
                operand_stack.append(a.union(b))
            elif operators[op] == 'intersection':
                operand_stack.append(a.intersection(b))
            elif operators[op] == 'difference':
                operand_stack.append(a.difference(b))
            elif operators[op] == 'symmetric_difference':
                operand_stack.append(a.symmetric_difference(b))

    if len(operand_stack) != 1:
        return None, f"Error: Expresión mal formada, operand stack final: {[sorted_set_str(s) for s in operand_stack]}"

    result = operand_stack[0]
    result_str = ' '.join(tokens)
    for key, value in set_map.items():
        result_str = result_str.replace(key, sorted_set_str(value, sort_output))
    result_str += f" = {sorted_set_str(result, sort_output)}"
    return result, result_str

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    set1_str = data.get('set1', '')
    set2_str = data.get('set2', '')
    set3_str = data.get('set3', '')
    expression = data.get('expression', '')
    sort_output = data.get('sortOutput', True)

    print(f"Expresión recibida: '{expression}'")
    print(f"Conjunto A recibido: '{set1_str}'")
    print(f"Conjunto B recibido: '{set2_str}'")
    print(f"Conjunto C recibido: '{set3_str}'")
    
    sets = [parse_set(set1_str), parse_set(set2_str), parse_set(set3_str)]
    result, result_str = evaluate_expression(expression, sets, sort_output)
    if result is None:
        return jsonify({'result': 'Error', 'error': result_str, 'isEmpty': False})

    return jsonify({
        'result': result_str,
        'isEmpty': len(result) == 0
    })

if __name__ == '__main__':
    app.run(debug=True)
    