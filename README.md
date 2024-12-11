# Boolgebra

Domain Specific Language based on Boolean Algebra Simplification

## Motivation 

It's not always easy to get the correct simplified boolean expression. This project tries to help students with boolean algebra by producing the correct simplified expression, which is used to check answers.

## example.boolgebra

    let expr = A + A'
    simplify expr

    Output:
    expr = A + A'
    simplified expr: 1
    
## Brief Overview of Functions

    'let' (ASSIGNMENT)
    'simplify' (BOOL SIMPLIFICATION)
    'compare' (EQUALITY)
    'truthtable' (PRINT TRUTHTABLE)
