import re
from textx import metamodel_from_file
from sympy import symbols
from sympy.logic.boolalg import And, Or, Not, Equivalent, simplify_logic
from itertools import product


boolgebra_mm = metamodel_from_file('syntax.tx')
boolgebra_model = boolgebra_mm.model_from_file('text.boolgebra')

variables = {}

def parseLiteral(stringLiteral):
    terms = r"([A-Z])('?)"
    tokens = re.findall(terms, stringLiteral)
    literals = []
    for var, boolean_not in tokens:
        literals.append((var, boolean_not == "'"))
    return literals

def parseExpression(expression):
    expressionList = []
    for i in expression:
        literals = parseLiteral(i)
        term = set(literals)
        expressionList.append(term)
    return expressionList

def sympyExpression(expression):
    variables = set(j[0] for i in expression for j in i)
    sympyVariables = {v: symbols(v) for v in variables}

    or_terms = []
    for term in expression:
        and_literals = []
        for (w, boolean_not) in term:
            lit = Not(sympyVariables[w]) if boolean_not else sympyVariables[w]
            and_literals.append(lit)
        if and_literals:
            or_terms.append(And(*and_literals))
        else:
            or_terms.append(True)

    if not or_terms:
        return False
    return Or(*or_terms)

def expressionAsString(simplifiedExpr):
    basicExpression = simplify_logic(simplifiedExpr)
    if basicExpression == True:
        return "1"
    elif basicExpression == False:
        return "0"
    
    #Disjunctive Normal Form 
    dnfExpression = simplify_logic(simplifiedExpr, form='dnf')
    if dnfExpression == True:
        return "1"
    elif dnfExpression == False:
        return "0"

    def literal_to_str(literal):
        if literal.is_Symbol:
            return str(literal)
        elif literal.func == Not:
            return str(literal.args[0]) + "'"
        else:
            return str(literal)

    if isinstance(dnfExpression, Or):
        terms = dnfExpression.args
    else:
        terms = [dnfExpression]

    term_str_list = []
    for t in terms:
        if t == True:
            term_str_list.append("1")
            continue
        if t == False:
            term_str_list.append("0")
            continue
        if isinstance(t, And):
            lits = [literal_to_str(l) for l in t.args]
        else:
            lits = [literal_to_str(t)]
        term_str_list.append("".join(lits))

    return " + ".join(term_str_list)

def simplifyString(expression):
    expressionList = parseExpression(expression)
    sympy_expr = sympyExpression(expressionList)
    simplified_expr = simplify_logic(sympy_expr, form='dnf')
    return expressionAsString(simplified_expr)

def print_truth_table(sympy_expr):
    variables = list(sympy_expr.free_symbols)
    variables.sort(key=lambda x: x.name)

    header = " | ".join(v.name for v in variables) + " | Out"
    print(header)
    
    for val in product([False, True], repeat=len(variables)):
        assignment = dict(zip(variables, val))
        result = sympy_expr.subs(assignment)
        row = " | ".join('1' if val else '0' for val in val) + " | " + ('1' if result else '0')
        print(row)
    
def interpret(model):
    for c in model.commands:
        if c.__class__.__name__ == "AssignmentCommand":
            for e in c.expr:
                if not re.match(r"^[A-Z](')?([A-Z](')?)*$", e.term):
                    print(f"Error: '{e.term}' is invalid. Use only uppercase letters and optional '.")
                    return
            expression = " + ".join(e.term for e in c.expr)
            variables[c.var] = c.expr
            print(f"{c.var} = {expression}")

        elif c.__class__.__name__ == "SimplifyCommand":
            if c.var not in variables:
                print(f"Error: variable '{c.var}' not defined.")
                return
            original_expr = variables[c.var]
            simplified_expr = simplifyString([e.term for e in original_expr])
            print(f"Simplified {c.var}: {simplified_expr}")

        elif c.__class__.__name__ == "CompareCommand":
            if c.var1 not in variables:
                print(f"Error: variable '{c.var1}' not defined.")
                return
            if c.var2 not in variables:
                print(f"Error: variable '{c.var2}' not defined.")
                return

            expr1 = parseExpression([e.term for e in variables[c.var1]])
            expr2 = parseExpression([e.term for e in variables[c.var2]])

            sym1 = sympyExpression(expr1)
            sym2 = sympyExpression(expr2)

            simplified1 = simplify_logic(sym1)
            simplified2 = simplify_logic(sym2)

            eq_expr = Equivalent(simplified1, simplified2)
            eq_simplified = simplify_logic(eq_expr)
            if eq_simplified == True:
                print(f"{c.var1} is equivalent to {c.var2}")
            else:
                print(f"{c.var1} is not equivalent to {c.var2}")

        elif c.__class__.__name__ == "TruthTableCommand":
            if c.var not in variables:
                print(f"Error: variable '{c.var}' not defined.")
                return
            expression = parseExpression([e.term for e in variables[c.var]])
            sympy_expr = sympyExpression(expression)
            print_truth_table(sympy_expr)
            

interpret(boolgebra_model)
