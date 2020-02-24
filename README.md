# MDC Lang

## Built-in Regex Strings

With MDCL, Regex is built-in. You can make Regex Strings by converting Strings
to Regex with the `REGEX` function, or by typing `RE` before a set of quotes
to automatically compile the text within the quotes into a Regex String.

## Intuitive Keywords

There is a list of different keywords which can be placed between two values
that perform a different action depending on the datatypes of the two values.

List of current keywords:

- ADD
- SUB
- MULT
- DIV
- PWR
- MOD
- EQ
- LT
- GT
- LE
- GE
- INDEX
- HAS

There are shorthands for most keywords, which include the following:

`+` - ADD
`-` - SUB
`*` - MULT
`/` - DIV
`^` - PWR
`%` - MOD
`=` - EQ
`|` - INDEX

Putting the `ADD` keyword (or just `+`) between two Integers will add both
Integers together, and return the result as an Integer:

    63 + 17;

    -> `80`

A more complex example would be using two Strings with the `DIV` keyword
(or `/`) to count how many times the right hand String occurs in the
left hand String:

    'the cat sat on the mat' / 'the';

    -> `2`

## Datatypes

The current most common Datatypes in MDCL include:

### Integer
-----------

Integers are assigned with any positive (eg 1 or +1) or negative (eg -1)
numeric value, or by using the `INTEGER` function.

### Float
---------

Floats can be assigned with any positive or negative numeric value with a
floating point, similar to the way Integers are assigned, or with the `FLOAT`
function.

An example of a Float assignment could be `3.14159`, `.5`, or `6.`.

### String
----------

A String is a list of characters put together to form one 'string' of
characters, for example: "this is a string". Strings can be assigned in a few
different ways.

Making single quote Strings, or Raw Strings ('like this') will make a String
that evaluates every character exactly how you see it within the single quotes.
In further detail, if you enter a backslash or newline character into a
Raw String, you will see `\` or `\n` being printed to the console when you echo
the String's value.

Making double quote String ("like this") is the equivalent to how Strings work
in most languages. Backslash plus a lowercase 'n' will evaluate to a newline
character, and backslashes will be used as escape characters.

The final way you can assign a String is by using the `STRING` function, which
will evaluate to an empty String unless given arguments to tell otherwise.

### RegexString
---------------

A Regex String is a datatype that holds a compiled Regex Expression within it,
and it can be used to evaluate whether other Strings match with it's own
compiled Regex Expression.

Regex Strings can be assigned by placing `RE` before a String, or by using the
`REGEX` function with a String argument.

### Boolean
-----------

Booleans are always either 0 or 1, 0 being `FALSE` and 1 being `TRUE`.

Booleans can be assigned with the `BOOLEAN` function with any argument, or by
using the `TRUE` or `FALSE` keywords.

### Null
--------

Null is the standard placeholder for something with no value. Null evaluates
to `FALSE` in Boolean form, or `NULL` in String form.

The Null value is returned from functions which don't have any `YIELD` or
`RETURN` statements. You can also manually assign a variable to Null by typing
`NULL`, or if you want to be fancy, omitting the variable value entirely.

For example, omitting the value:

    x : ;

OR:

    x:;

in both of these lines, `x` is `NULL`. It's still a variable, it exists and you
can use it without causing an error, but it's equal to `NULL`.

### Array
---------

Arrays are a list of other datatypes combined, each with their own indexes.

When printing Arrays, you receive a list of their values converted to Strings
and separated by commas, and enclosed with `(` and `)`.

String output of an Array with numbers from 0 to 10:

    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

Arrays can be assigned through a number of different methods. To assign an
empty Array, use the `ARRAY` keyword with no arguments, and you'll have
yourself an empty Array. There a few built-in functions that return Arrays,
as show below.

Using the `TO` keyword to initialise an Array:

    1 TO 10;

    -> (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

You can also use the `SKIP` keyword to skip items in an Array and produce a
new Array:

    0 TO 10 SKIP 2;

    -> (0, 2, 4, 6, 8, 10)

When yielding with the `YIELD` keyword within a function more than once, all
yielded values are returned as an Array.

## Object Oriented Programming

OOP!

MDCL currently has the ability to create Objects, to an extent. Objects right
now are just NULL values with attributes assigned within them, and with the
ability to call functions and values with the usage of keywords.

The best way to create an Object isn't clear at the moment, but there are
currently MANY different ways to do so.

One time example with minimal indentation, using `NULL`:

    obj:;
    obj.importantStuff : ARRAY;
    obj.doThings : [] => { YIELD; };

    !ECHO obj.importantStuff;
    !obj.doThings;

This example looks less like an Object being created and more like a
dictionary, with `.key` instead of `[key]`. In a way, this is what
is happening in this example. But there's a bit more to it, have a look below:

Multi-use example with minimal indentation, using `NULL`:

    Square : [size,] => {
        sq : ;
        sq.size : size;
        sq.getSize : [self,] => { !ECHO self.size };
        YIELD sq;
    };

    square : !Square 4;
    !ECHO square.size;
    !square.getSize square;

This example shows a function which creates a NULL value and assigns some
values to it, which looks like it's getting closer to being a real Object.

And then you get to this point, which is about as far as MDCL can go with
Object creation right now. This is closer to class creation in Python than
the previous examples:

    Square : [size,] => {
        self.size : size;

        self.ADD : [self, other] => {
            self.size +: 1;
            YIELD self;
        };

        YIELD self;
    };

    square : !Square 4;
    !ECHO square.size;
    square +: 1;
    !ECHO square.size;

A little more familiar, right?
