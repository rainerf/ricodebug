Coding Style
=========


# 1. Introduction

This document should be used as a guideline, and provides coding conventions for the ricodebug-project. The project was initialized by the Upper Austria University of Applied Sciences, department of Hardware/Software-Design. The following coding-style should be followed by anyone, who wants to contribute to the ricodebug-project. Based on the PEP8 coding style, it should provide a simple and efficient way of coding. The aim of this document is to improve readability and consistency of the source code.

# 2. Code lay-out

## 2.1 Indentation
Use 4 spaces per indentation level and no tabs.

Never mix tabs and spaces.

Continuation lines should align wrapped elements either vertically using Python's implicit line joining inside parentheses, brackets and braces, or using a hanging indent. When using a hanging indent the following considerations should be applied; there should be no arguments on the first line and further indentation should be used to clearly distinguish itself as a continuation line.

~~~~~~~~~~~~~{.py}
Yes:

# Aligned with opening delimiter
foo = long_function_name(var_one, var_two,
                         var_three, var_four)

# More indentation included to distinguish this from the rest.
def long_function_name(
        var_one, var_two, var_three,
        var_four):
    print(var_one)
No:

# Arguments on first line forbidden when not using vertical alignment
foo = long_function_name(var_one, var_two,
    var_three, var_four)

# Further indentation required as indentation is not distinguishable
def long_function_name(
    var_one, var_two, var_three,
    var_four):
    print(var_one)
~~~~~~~~~~~~~

## 2.2 Tabs or Spaces?
Never mix tabs and spaces!

Always use 4 spaces per indentation level, and avoid using tabs.

## 2.3 Maximum Line Length
The preferred way of wrapping long lines is by using Python's implied line continuation inside parentheses, brackets and braces. Long lines can be broken over multiple lines by wrapping expressions in parentheses. These should be used in preference to using a backslash for line continuation. Make sure to indent the continued line appropriately. The preferred place to break around a binary operator is after the operator, not before it.

## 2.4 Blank Lines
Separate top-level function and class definitions with two blank lines.

Method definitions inside a class are separated by a single blank line. 

Extra blank lines may be used (sparingly) to separate groups of related functions. Blank lines may be omitted between a bunch of related one-liners (e.g. a set of dummy implementations). 

Use blank lines in functions, sparingly, to indicate logical sections.

## 2.5 Encodings
Code should always use the UTF-8 encoding. 

## 2.6 Imports
Imports should usually be on seperate lines, e.g.:

~~~~~~~~~~~~~{.py}
Yes: import os
     import sys

No:  import sys, os
~~~~~~~~~~~~~

It's okay to say this though:
~~~~~~~~~~~~~{.py}
from subprocess import open, PIPE
~~~~~~~~~~~~~

Imports are always put at the top of the file, just after any module comments and docstrings, and before module globals and constants.

Imports should be grouped in the following order:
 
standard library imports
 
related third party imports
 
local application/library specific imports
 
You should put a blank line between each group of imports. 

When importing a class from a class-containing module, it's usually okay to spell this:
~~~~~~~~~~~~~{.py}
from myclass import MyClass
from foo.bar.yourclass import YourClass
~~~~~~~~~~~~~

# 3. Whitespace in Expressions and Statements
Always avoid extraneous whitespace in the following situations: 
- Immediately inside parentheses, brackets or braces.
  ~~~~~~~~~~~~~{.py}
  Yes: spam(ham[1], {eggs: 2})
  No:  spam( ham[ 1 ], { eggs: 2 } )
  ~~~~~~~~~~~~~

- Immediately before a comma, semicolon, or colon:
  ~~~~~~~~~~~~~{.py}
  Yes: if x == 4: print x, y; x, y = y, x
  No:  if x == 4 : print x , y ; x , y = y , x
  ~~~~~~~~~~~~~
- Immediately before the open parenthesis that starts the argument list of a function call:
  ~~~~~~~~~~~~~{.py}
  Yes: spam(1)
  No:  spam (1)
  ~~~~~~~~~~~~~
- Immediately before the open parenthesis that starts an indexing or slicing:
  ~~~~~~~~~~~~~{.py}
  Yes: dict['key'] = list[index]
  No:  dict ['key'] = list [index]
  ~~~~~~~~~~~~~
- More than one space around an assignment (or other) operator to align it with another.
  ~~~~~~~~~~~~~{.py}
  Yes:

  x = 1
  y = 2
  long_variable = 3

  No:

  x             = 1
  y             = 2
  long_variable = 3
  ~~~~~~~~~~~~~

Always surround these binary operators with a single space on either side: assignment (=), augmented assignment (+=, -= etc.), comparisons (==, <, >, !=, <>, <=, >=, in, not in, is, is not), Booleans (and, or, not). 

Use spaces around arithmetic operators:
~~~~~~~~~~~~~{.py}
Yes:

i = i + 1
submitted += 1
x = x * 2 - 1
hypot2 = x * x + y * y
c = (a + b) * (a - b)
No:

i=i+1
submitted +=1
x = x*2 - 1
hypot2 = x*x + y*y
c = (a+b) * (a-b)
~~~~~~~~~~~~~

# 4. Comments
Comments that contradict the code are worse than no comments. Always make a priority of keeping the comments up-to-date when the code changes! 

Comments should be complete sentences. If a comment is a phrase or sentence, its first word should be capitalized, unless it is an identifier that begins with a lower case letter (never alter the case of identifiers!). 

Code-sections or Functions that need to be fixed can be marked by the following comment:
~~~~~~~~~~~~~{.py}
# FIXME
~~~~~~~~~~~~~

Code-sections that need to be done can be highlighted by the following comment:
~~~~~~~~~~~~~{.py}
# TODO
~~~~~~~~~~~~~

## 4.1 Block comments
Block comments generally apply to some (or all) code that follows them, and are indented to the same level as that code. Each line of a block comment starts with a # and a single space (unless it is indented text inside the comment).

Paragraphs inside a block comment are separated by a line containing a single #.

## 4.2 Inline comments
Inline-comments should be avoided at any time. If the programmer wants to comment a single line of code, he should place the comment in the line above the code!

## 4.3 Doc strings
Write docstrings for all public modules, functions, classes, and methods. 

Docstrings always are placed one line under the declaration of the class, function, method, etc. 

They begin with and also end with three quotation marks. There is no blank line either before and after the docstring. 

For one liner docstrings, it's okay to keep the closing on the same line.
~~~~~~~~~~~~~{.py}
def function(a, b):
    """Do X and return a list."""
~~~~~~~~~~~~~


# 5 Naming conventions
Always use self as the name of the first method argument.

## 5.1 Module names
Modules should have short, all-lowercase names. Underscores can be used in the module name, instead of spaces, if it improves readability. Python packages should also have short, all-lowercase names.

## 5.2 Variable and function names
Variable names and function names should be lower camelCase.

## 5.3 Class names
Almost without exception, class names use the CapWords convention. Classes for internal use have a leading underscore in addition.

## 5.4 Constants
Constants are usually defined on a module level and written in all capital letters with underscores separating words. Examples include MAX_OVERFLOW and TOTAL.

# 6 Programming recommendations

- Code should be written in a way that does not disadvantage other implementations of Python (PyPy, Jython, IronPython, Cython, Psyco, and such).

- Comparisons to singletons like None should always be done with is or is not, never the equality operators.

- Use string methods instead of the string module.

- Use ''.startswith() and ''.endswith() instead of string slicing to check for prefixes or suffixes.

- startswith() and endswith() are cleaner and less error prone. For example:
  ~~~~~~~~~~~~~{.py}
  Yes: if foo.startswith('bar'):
  No:  if foo[:3] == 'bar':
  ~~~~~~~~~~~~~

- Object type comparisons should always use isinstance() instead of comparing types directly.
  ~~~~~~~~~~~~~{.py}
  Yes: if isinstance(obj, int):
  
  No:  if type(obj) is type(1):
  ~~~~~~~~~~~~~

- checking if an object is a string, keep in mind that it might be a unicode string too! In Python 2.3, str and unicode have a common base class,   basestring, so you can do:
  ~~~~~~~~~~~~~{.py}
  if isinstance(obj, basestring):
  ~~~~~~~~~~~~~

- For sequences, (strings, lists, tuples), use the fact that empty sequences are false.
  ~~~~~~~~~~~~~{.py}
  Yes: if not seq:
       if seq:
  
  No: if len(seq)
      if not len(seq)
  ~~~~~~~~~~~~~

- Don't write string literals that rely on significant trailing whitespace. Such trailing whitespace is visually indistinguishable and some editors (or more recently, reindent.py) will trim them.

- Don't compare boolean values to True or False using ==.
  ~~~~~~~~~~~~~{.py}
  Yes:   if greeting:
  No:    if greeting == True:
  Worse: if greeting is True:
  ~~~~~~~~~~~~~

