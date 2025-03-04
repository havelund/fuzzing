
# Grammar

## Notation

The grammar for the temporal logic uses the following notation:

- `<term>` : a non-terminal
- `<term> ::=` ... : definition of a non-terminal
- `... | ...` : choice between alternatives 
- `<term>?` : 0 or 1 occurrence
- `<term>*` : 0 or more occurrences
- `":"` a symbol
- `IMPLIES` : all capital word indicates a keyword or symbol, see table below

## The Grammar

```python
<spec>::= <rule>*

<rule> ::= RULE ID ":" <formula>

<formula> ::= 
          <formula> IMPLIES <formula>  
        | ID "(" <constraints>? ")" (IFTHEN | ANDTHEN) <formula>
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
        | <expression> RELOP <expression>
        | <expression> RELOP <expression> RELOP <expression>
        | "(" <formula> ")"
        | "true"
        | "false"
        | COUNT "(" INT "," INT ")" <formula>
        | COUNTPAST   "(" INT "," INT ")" <formula>
        | COUNT INT  <formula> 
        | COUNTPAST INT <formula>
        | <formula THEN <formula>
        | <formula AFTER <formula>
        
<expression> ::= ID | INT | FLOAT | STRING

<constraints> ::= <constraint> ("," <constraint>)*

<constraint> ::= 
            ID "=" ID
          | ID "=" ID "?" 
          | ID "=" INT 
          | ID "=" FLOAT
          | ID "=" STRING
```

## Table of Keywords and Symbols

Keywords have an alternative symbol representation.

| Token      | Syntax            |
|------------|-------------------|
|  `RULE`    | rule          , norule |
| `NOT`      | not           , ! |
| `IMPLIES`  | implies       , -> |
| `OR`       | or            , \| |
| `AND`      | and           , & |
| `ALWAYS`   | always        , [] |
| `EVENTUALLY` | eventually  , <>  |
| `UNTIL`    | until         , U |
| `WUNTIL`   | wuntil        , WU |
| `NEXT`     | next          , () |
| `WNEXT`    | wnext         , ()? |
| `SOFAR`    | sofar         , [*] |
| `ONCE`     | once          , <*> |
| `SINCE`    | since         , S |
| `WSINCE`   | wsince        , WS |
| `PREV`     | prev          , (*) |
| `WPREV`    | wprev         , (*)? |
| `IFTHEN`   | ifthen        , => |
| `ANDTHEN`  | andthen       , &> |
| `THEN`     | then          , ~> |
| `AFTER`    | after         , ~*> |
| `COUNT`    | count         , @ |
| `COUNTPAST` | countpast    , @* |
| `RELOP`    | <             , <= , = , != , >= , > |
| `REQUIRED` | ?             , ! |