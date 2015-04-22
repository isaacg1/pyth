2. More Details About Pyth
**************************

Since you now have the programming environment set up to program in, let's learn some more about the language. Let's try adding some numbers now.

2.1. Pyth Uses Prefix Notation
==============================

Ok, ``2+2`` seems easy enough. Check and see what the interpreter makes of that. It'll be 4 right?::

	2
	Traceback (most recent call last):
	  File "safe_pyth.py", line 300, in <module>
	  File "<string>", line 5, in <module>
	TypeError: plus() missing 1 required positional argument: 'b'

Oh noes! An error! What went wrong? Well, Pyth doesn't use Infix notation like most languages do (the operator goes between the operands), but instead uses `Prefix (aka Polish) <http://en.wikipedia.org/wiki/Polish_notation>`_ notation, which means the operator goes *before* the operands. This has the benefit of not requiring parenthesis, making programs shorter and freeing up operators for other use. So let's try that math problem again::

	+2 2
	
	Output:

	4

There, now its working like we expected it to. Notice the space between the ``2``'s so the parser doesn't interpret them as a ``22``.

2.2. Pyth Has Many, Many Operators
==================================

The addition operator we just saw doesn't even begin to scratch the surface of Pyth's rich variety of operators. Besides addition Pyth has all the customary arithmetic operators - ``-`` for subtraction, ``*`` for multiplication, ``/`` for division, ``%`` for modulo, and ``^`` for exponentiation. Integers are defined as you would expect and Floats with the decimal point. Ex::

	0
	1
	18374
	2.5

However, negative numbers do not use a unary version of the subtraction symbol since all operators have a fixed arity (more on that later) but use the unary reversal operator: ``_``::

	Invalid: -25

	Valid: _25

Pyth also has predefined variables that are set to useful values before program execution starts. Examples are::

	Z=0
	T=10
	k=""
	d=" "
	b="\n"

All operators, variables, and control flow keywords, are always one character long to reduce the size of the program. This does make Pyth programs very hard to read.

As I said before, Pyth has much more than arithmetic, but you'll learn about them in due time.

2.3. All Operators in Pyth Have a Fixed Arity
=============================================

A very important concept in Pyth is that of arity. The `arity <http://en.wikipedia.org/wiki/Arity>`_ of an operator or function (according to Wikipedia) is *the number of arguments or operands the function or operation accepts.* Most programming languages allow functions to accept different amounts of arguments, but this causes them to require parenthesis. In the want for smaller programs, Pyth has a fixed number of operands per operator, allowing it to do away with parenthesis or any other delimiter.

2.4. Operators Mean Different Things in Different Contexts
==========================================================

In an effort to further increase the number of function available with only one character operators, operators do different things in Pyth depending on the values passed to it. For example, the ``+`` operator adds numbers, which you already saw, but if it gets two sequences (e.g. strings, lists) as operands, it concatenates them::

	+2 T -> 12 (remember that T=10)

	+"Hello ""World!" -> Hello World!

The ``+`` sign meaning both concatenation and addition is pretty common, but Pyth takes this to another level, with most operators having 2 or more meanings.

2.5. The Pyth Code is Compiled to Python Code Then Run
======================================================

Pyth is technically a `JIT <http://en.wikipedia.org/wiki/Just-in-time_compilation>`_ compiled language since the Pyth code is converted to Python through a series of rules defined in the file ``data.py`` and then run with the variables and functions defined in ``macros.py``. To see this in action, you can select the debug button in the online interpreter or pass the ``-d`` flag to the local one to see the compiled Python code. Here is what comes out as debug from ``^T6`` which evaluates to a million::

	==================================================
	^T6
	==================================================
	Pprint("\n",Ppow(T,6))
	==================================================
	1000000

As you can see, the exponentiation call is translated to a call to the function ``Ppow`` and is implicitly printed through a custom print function called ``Pprint``. The debug option can be very helpful with seeing what at first glance looks like a bunch of random characters does.

Next we'll write some example programs to learn more about Pyth.