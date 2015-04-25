5. Learning More - Documentation and Errors
****************************

5.1. Documentation
==================

Now you've got a basic grasp of Pyth. Going forward from here, the best way to learn more about the language is via the documentation. Pyth's documentation is located `on Github <https://raw.githubusercontent.com/isaacg1/pyth/master/doc.txt>`_, and is updated continuously as the language evolves. A representative line from the documentation looks like this::

    @  2 N lookup            Lookup from str, list or dict. Modulo wrapping on list, str.
                             On seq, seq, intersection.
                             Specifically, filter second arg on presence in first arg.
                             On num, num, bth root of a.

Let's break down what this says piece by piece.

* The first field, which is ``@`` here, is the name of the function in question.
* The second field, ``2`` in this case, is the arity of the function. So we have the function ``@``, which takes 2 arguments.
* The next field says whether printing is suppressed for this function. ``N`` means that printing is normal. An example of a token which suppresses printing is ``F``, the for loop. It wouldn't make sense to try to print a for loop.
* Next, we have a (hopefully) more memorable name for the function. This usually describes the most common usage of the function. In this case, the ``@`` function is most associated with the lookup functionality, also known as indexing.
* Finally, we have the full description of the function.

While the documentation is a good first step towards understanding how a function works, the only way to get a full understanding is by using it. Write programs using that function, and it'll become clear.

5.2. Errors
===========

Alright, so now you're trying out ``@``, and running some test programs. Inevitably, you're going to get some errors. There are two types of errors you might get: errors at the Pyth level, and errors at the Python level.

5.2.1 Pyth Errors
=================

Currently, there are only 3 types of errors implemented in Pyth: token not implemented errors, unsafe input errors, and wrong type errors. I'll go through these one by one.

Token not implemented errors occur when you try to use a token that Pyth has not yet implemented. They look like this::

    ==================== 6 chars =====================
    5.@1 1
    ==================================================
    Traceback (most recent call last):
      File "pyth.py", line 454, in <module>
        py_code_line = general_parse(code)
      File "pyth.py", line 38, in general_parse
        parsed, code = parse(code)
      File "pyth.py", line 105, in parse
        raise PythParseError(active_char, rest_code)
    extra_parse.PythParseError: .@ is not implemented, 4 from the end.

These are most commonly caused by using non-ASCII characters in Pyth code outside of strings, and by ending floating point numeric literals with a ``.``, which is confused with tokens of the form ``._``, as seen above.

Unsafe input errors occur only when you try to use ``$``, the python code injection character, in the online compiler / executor or when the ``-s``, safe mode, flag is enabled. It is an inherent security hole, and is therefore disabled online.

Wrong type errors are the most common in Pyth. Most of Pyth's functions are defined via type overloading, where the function does something entirely different depending on what types are given as input. However, not all combinations of types have an associated functionality. For instance::

    ==================== 9 chars =====================
    @"abc"1.5
    ==================================================
    Pprint("\n",lookup("abc",1.5))
    ==================================================
    Traceback (most recent call last):
      File "pyth.py", line 478, in <module>
      File "<string>", line 4, in <module>
      File "/app/macros.py", line 84, in lookup
    macros.BadTypeCombinationError: 
    Error occured in function: @
    Arg 1: 'abc', type str.
    Arg 2: 1.5, type float.

The relevant part to look at is the last four lines. The fourth to last line indicates that an error as caused due to a bad type combination. The third to last line indicates that the error occurred in the ``@`` function, and the rest of the lines indicate that the error occurred because ``@`` was called with a string as its first argument and a float as its second argument, for which it has no defined functionality.

5.2.2 Python Errors
===================

This is the everything else category. Something went wrong, and the function didn't work. At this point, the best solution is to simply try different variants on the program in an attempt to understand how it ticks. If that doesn't work, the only recourse is to look at the code itself. The error message will tell you on what line of what file something went wrong. For instance::

    ==================== 4 chars =====================
    @""1
    ==================================================
    Pprint("\n",lookup("",1))
    ==================================================
    Traceback (most recent call last):
      File "pyth.py", line 478, in <module>
      File "<string>", line 4, in <module>
      File "/app/macros.py", line 73, in lookup
    ZeroDivisionError: integer division or modulo by zero

This error is not very helpful. Why is string indexing throwing a divide by zero error? Referring to the line mentioned in the error message, line 73 of macro.py, tells us that ``@`` attempts to perform a lookup in the string at the index given by the second argument modulus the length of the string. Since the length of the string is zero, the above error is thrown.

This method should only be used as a last resort, but is occasionally necessary when all else fails. On the other hand, if you're comfortable with looking through the Pyth source code, you might be able to improve Pyth.
