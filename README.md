# MDC Lang

## Built-in Regex Strings

With MDC, Regex is built-in. You can make Regex Strings by converting Strings or Raw Strings to Regex with the `REGEX` keyword, or you can type `RE` before a set of quotes to automatically compile the text within the quotes into a Regex String.

## Intuitive Keywords

There is a list of different keywords which can be placed between two values that perform a different action depending on the datatypes of the two values.

For example, putting the `ADD` keyword between two Integers will add both Integers together, and return the result as an Integer:

    63 ADD 17;

Returns: `80`

A more complex example would be using two Strings surrounding the `DIV` keyword to count how many times the right hand String occurs in the left hand String:

    'the cat sat on the mat' DIV 'the';

Returns: `2`

List of current keywords:

- ADD
- SUB
- MULT
- DIV
- PWR
- EQ
- LT
- GT
- LE
- GE
- INDEX
- HAS

## Datatypes

The current Datatypes in MDC include:

### Integer
-----------

Integers are assigned with any positive (eg 1 or +1) or negative (eg -1) numeric value, or using the `INTEGER` keyword.

### Float
---------

Floats currently can not be assigned through any means other than the `FLOAT` keyword.
Floats are numeric positive or negative values similar to Integers except that they have a floating point, or more commonly a decimal point.

### String
----------

A String is a list of characters put together to form one value, for example: "this is a string". Strings can be assigned in a few different ways.

Making single quote Strings, or Raw Strings ('like this') will make a String that evaluates every character exactly how you see it within the single quotes. In further detail, if you enter a backslash or newline character into a Raw String, you will see \ or \n being printed to the console when you echo it's value.

Making double quote String ("like this") is the equivalent to how Strings work in most languages. Backslash plus a lowercase 'n' will evaluate to a newline character, and backslashes will be used as escape characters.

The final way you can assign a String is by using the `STRING` keyword, which will evaluate to an empty String unless given arguments to tell otherwise.

### RegexString
---------------

A Regex String is a datatype that holds a compiled Regex Expression within it, and can be used to evaluate whether other Strings match with it's own compiled Regex Expression.

Regex Strings can be assigned by placing `RE` before a set of quotes, or by using the `REGEX` keyword with a String argument.

### Boolean
-----------

Booleans are always either 0 or 1, 0 being `FALSE` and 1 being `TRUE`.

Booleans can be assigned with the `BOOLEAN` keyword with any argument, or using the `TRUE` or `FALSE` keywords.

When printing a Boolean to the console, it will return it's value as `TRUE` or `FALSE`, but when put into the `INTEGER` keyword, it will return it's value as 0 or 1.

### Null
--------

Null is the standard placeholder for something with no value. Null evaluates to `FALSE`, or `NULL` in String form.

The Null value is returned from functions which don't have any `YIELD` statements. You can also manually assign a variable to Null by typing `NULL`.

### Array
---------

Arrays are a list of other datatypes combined, each with their own indexes.

When printing Arrays, you receive a list of their values converted to Strings and separated by commas, and enclosed with '[' and ']'.

String output of an Array with numbers from 0 to 10:

    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

Arrays can be assigned through a number of different methods. To assign an empty Array, assign a variable to the `ARRAY` keyword, and it will be initialised with an empty Array. There a few built-in functions that return Arrays, as show below.

Using the `TO` keyword to initialise an Array:

    1 TO 10;

    -> [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

You can also use the `SKIP` keyword to skip items in an Array and produce a new Array:

    0 TO 10 SKIP 2;

    -> [0, 2, 4, 6, 8, 10]
