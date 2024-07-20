import ply.lex as lex
import ply.yacc as yacc


tokens = (
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'GREATER',
    'LESS',
    'EQUALS',
    'IF',
    'ELSE',
    'PRINT',
    'COLON',
    'COMMA',
    'STRING',
    'NAME',
    'AND',
    'OR',
)


t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_GREATER = r'>'
t_LESS = r'<'
t_EQUALS = r'=='
t_IF = r'if'
t_ELSE = r'else'
t_PRINT = r'print'
t_COLON = r':'
t_COMMA = r','
t_STRING = r'\".*?\"'
t_AND = r'and'
t_OR = r'or'


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = 'NAME'
    return t


t_ignore = ' \t'


def t_error(t):
    print("Caractere ilegal '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()


precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)


def p_expression_plus(p):
    'expression : expression PLUS expression'
    p[0] = p[1] + p[3]

def p_expression_minus(p):
    'expression : expression MINUS expression'
    p[0] = p[1] - p[3]

def p_expression_times(p):
    'expression : expression TIMES expression'
    p[0] = p[1] * p[3]

def p_expression_divide(p):
    'expression : expression DIVIDE expression'
    p[0] = p[1] / p[3]

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]

def p_expression_and(p):
    'expression : expression AND expression'
    p[0] = p[1] and p[3]

def p_expression_or(p):
    'expression : expression OR expression'
    p[0] = p[1] or p[3]


def p_error(p):
    print("Erro de sintaxe na entrada!")


parser = yacc.yacc()


def transpile_to_c(python_code):
    c_code = "#include <stdio.h>\n\nint main() {\n"
    lines = python_code.split("\n")
    for line in lines:
        if "=" in line and "if" not in line and "else" not in line:
            variable, value = line.split("=")
            variable = variable.strip()
            value = value.strip()
            if '.' in value:
                c_code += f"    float {variable} = {value};\n"
            elif '"' in value or "'" in value:
                c_code += f'    char {variable}[] = {value};\n'
            else:
                c_code += f"    int {variable} = {value};\n"
        elif "print" in line:
            print_content = line[line.index("(") + 1:line.index(")")]
            if "%" in print_content:
                mask, variable = print_content.split("%")
                c_code += f'    printf("{mask}\\n", {variable.strip()});\n'
            else:
                if '"' in print_content or "'" in print_content:
                    c_code += f'    printf("%s\\n", {print_content});\n'
                else:
                    c_code += f'    printf("%d\\n", {print_content.strip()});\n'
        elif "if" in line:
            condition = line[line.index("if") + 2:line.index(":")]
            condition = condition.replace("and", "&&").replace("or", "||")
            c_code += f"    if ({condition.strip()}) {{\n"
        elif "else" in line:
            c_code += "    } else {\n"
        elif line.strip() == "":
            continue
        else:
            c_code += f"    {line.strip()}\n"

    c_code += "    return 0;\n}\n"
    return c_code


python_code = """
x = 5
y = 10
a = 5.5
b = a * x
if x > y and a < 0:
    z = x - y
else:
    z = x + y
print(b)
print("O valor de z é:", z)
"""


c_code = transpile_to_c(python_code)
print(c_code)
