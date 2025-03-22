
# Grammar

## Notation

The grammar for the temporal logic uses the following notation:

- `<term>` : a non-terminal
- `<term> ::=` ... : definition of a non-terminal
- `... | ...` : choice between alternatives 
- `<term>?` : 0 or 1 occurrence
- `<term>*` : 0 or more occurrences
- `<term>+` : 1 or more occurrences
- `":"`     : a symbol
- `(...)`   : grouping
- `IMPLIES` : all capital word indicates a keyword or symbol, see table below

The grammar is divided into the _main grammar_, and then a grammar
for _regular expressions_, separated out for ease of reading,
and because the regular expression grammar is interpreted differently wrt. white spaces.

## Main Grammar

```python
<spec> ::= <rule>*

<rule> ::= RULE ID ":" <formula>

<formula> ::= 
          <formula> IMPLIES <formula>  
        | ID "(" <constraints>? ")" (IFTHEN | ANDTHEN) <formula>
        | "[" ID "(" constraints? ")" "]" formula 
        | "<" ID "(" constraints? ")" ">" formula 
        | <formula> OR <formula>
        | <formula> AND <formula> 
        | ID "(" <constraints>? ")" 
        | ALWAYS <formula>
        | EVENTUALLY <formula> 
        | <formula> UNTIL <formula>
        | <formula> WUNTIL <formula>
        | <formula> SINCE <formula>
        | <formula> WSINCE <formula>
        | SOFAR <formula> 
        | ONCE <formula>
        | NEXT <formula>
        | WNEXT <formula> 
        | PREV <formula>  
        | WPREV <formula>  
        | NOT <formula> 
        | <expr> RELOP <expr>
        | <expr> RELOP <expr> RELOP <exp>
        | <expr> INREG <regular_expr>
        | "(" <formula> ")"
        | "true"
        | "false"
        | COUNT "(" INT "," INT ")" <formula>
        | COUNTPAST   "(" INT "," INT ")" <formula>
        | COUNT INT  <formula> 
        | COUNTPAST INT <formula>
        | <formula THEN <formula>
        | <formula AFTER <formula>
        
<expr> ::= ID | INT | FLOAT | STRING 
         | <expr> ("+"|"-"|"*"|"/") <expr> 
         | "(" <expr> ")"

<constraints> ::= <constraint> ("," <constraint>)*

<constraint> ::= 
             ID "=" ID
           | ID "=" ID "?" 
           | ID "=" INT 
           | ID "=" FLOAT
           | ID "=" STRING
```

### Table of Keywords and Symbols

Keywords have an alternative symbol representation.

| Token        | Syntax                               |
|--------------|--------------------------------------|
| `RULE`       | rule          , norule               |
| `NOT`        | not           , !                    |
| `IMPLIES`    | implies       , ->                   |
| `OR`         | or            , \|                   |
| `AND`        | and           , &                    |
| `ALWAYS`     | always        , []                   |
| `EVENTUALLY` | eventually  , <>                     |
| `UNTIL`      | until         , U                    |
| `WUNTIL`     | wuntil        , WU                   |
| `NEXT`       | next          , ()                   |
| `WNEXT`      | wnext         , ()?                  |
| `SOFAR`      | sofar         , [*]                  |
| `ONCE`       | once          , <*>                  |
| `SINCE`      | since         , S                    |
| `WSINCE`     | wsince        , WS                   |
| `PREV`       | prev          , (*)                  |
| `WPREV`      | wprev         , (*)?                 |
| `IFTHEN`     | ifthen        , =>                   |
| `ANDTHEN`    | andthen       , &>                   |
| `THEN`       | then          , ~>                   |
| `AFTER`      | after         , ~*>                  |
| `COUNT`      | count         , @                    |
| `COUNTPAST`  | countpast    , @*                    |
| `RELOP`      | <             , <= , = , != , >= , > |
| `REQUIRED`   | ?             , !                    |
| `INREG`      | matches       , \|-                  |

## Regular Expression Grammar

In this regular expression grammar, white spaces are significant 
and are treated as literal characters—unlike in the main grammar, 
where they are ignored. For example, the two white spaces in 
the notation "/" <union_expr> "/" are provided solely for 
clarity and should not be typed.

```python
<regular_expr> ::= "/" <union_expr> "/"

<union_expr> ::= <concat_expr> ("|" <concat_expr>)* 

<concat_expr> ::= <repeat_expr>+ 

<repeat_expr> ::= <atom_expr> <quantifier?

<atom_expr> ::= 
            "(" <regular_expr> ")"    
          | "[" <char_range>+ "]"  
          | "."                
          | "\d" | "\w" | "\s"            
          | <char>

<quantifier> ::= "*" | "+" | "?" | "{" INT ("," INT)? "}"  

<char_range> ::= <char> "-" <char> | <char>
```