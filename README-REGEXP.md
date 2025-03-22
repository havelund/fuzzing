
# Regular Expressions

A regular expression is enclosed with two `/`-symbols: `/.../` and can contain the following operators.

|   Formula    | Explanation                 | Example        |
|:------------:|-----------------------------|----------------|
|      .       | any character               | he..o          |
|     [ ]      | range                       | [A-Za-z012]    |
|      *       | zero or more                | [A-Z]*         |
|      +       | one or more                 | [A-Z]+         |
|      ?       | zero or one                 | [A-Z]?         |
| {m} or {m,n} | Number of occurrences       | [A-Z]{4,6}     |
|      \|      | Either or                   | data \| img    |
|      ()      | Group                       | (data \| img)? |
|      \d      | means [0-9]                 | \d             |
|      \w      | means [A-Za-z0-9_]          | \w             |
|      \s      | space                       | \s             |
|      \       | escape character in general | \\\            |

**Note** that a regular expression matches the **whole** string, corresponding to using Python's 
`re.fullmatch` function.

## Example

As an example, consider the following property stating that the message of a SEND command
must contain a file name within square brackets, consisting of a directory name starting with a letter, followed
by zero or more word letters, then a slash, then 3 digits, then a dot and then the name `data`
or the name `img`, and then an optional date after a dot of the form dddd-dd-dd, and finally more 
characters.

```python
rule p0 : <SEND(message=m?)> m matches /.*\[[A-Za-z]\w*\/[0-9]{3}\.(data|img)(\.\d{4}\-\d{2}\-\d{2})?\].*/
```

This rule may generate the following string for _m_:

```python
"B[m3Dl/228.data.4440-48-22]"
```

Let's break down and explain the regular expression:

|             Term             | Explanation                                              | 
|:----------------------------:|----------------------------------------------------------|
|              .*              | zero or more characters                                  |             
|             \\[              | [                                                        | 
|           [A-Za-z]           | A letter, capital or small                               | 
|             \\w*             | zero or more word letters                                | 
|             \\/              | /                                                        | 
|           [0-9]{3}           | 3 digits                                                 | 
|             \\.              | .                                                        | 
|       (data  \|  img)        | the word data or the word img                            |
| (\\.\\d{4}\\-\\d{2}\\-\\d2)? | optionally a . followed by a date of the form dddd-dd-dd | 
|             \\]              | ]                                                        | 
|              .*              | zero or more characters                                  | 

