9. The Language Specification - Sequences
*****************************************

This chapter of the specification deals with sequences. These are strings, arrays, tuples, etc. This chapter contains both sequence constructors and functions and operators that work on them.

9.1. " - String Literal
=======================

**Arity: Unbounded**

Starts a string literal. Stops parsing until it reaches a matching quote or EOF.

Ex::

	==================================================
	"abc""def
	==================================================
	Pprint("\n","abc")
	Pprint("\n","def")
	==================================================
	abc
	def

9.2. "[" - List Constructor
===========================

**Arity: Unbounded**

This starts a list definition. Elements are space-separated since the comma is the couple-constructor. Is ended like any other unbounded arity, with a ``)``. Lists are mutable.

Ex::

	==================================================
	[1 2 3)
	==================================================
	Pprint("\n",Plist(1,(2),(3)))
	==================================================
	[1, 2, 3]

9.3. "(" - Tuple Contructor
===========================

**Arity: Unbounded**

This starts a tuple definition. It works in the same way as the list constructor. Unlike lists, tuples are immutable.

Ex::

	==================================================
	(1 2 3)
	==================================================
	Pprint("\n",Ptuple(1,(2),(3)))
	==================================================
	(1, 2, 3)

9.4. "{" - Set Constructor
==========================

**Arity: 1**

This is the Python set constructor ``set()``. It takes a sequence and makes a set out of it. An important consequence for golfing is that all duplicates are removed when a set is created. On numbers it makes a one element set containing the number.

Ex::

	==================================================
	{[1 2 3){T
	==================================================
	Pprint("\n",Pset(Plist(1,(2),(3))))
	Pprint("\n",Pset(T))
	==================================================
	{1, 2, 3}
	{10}

9.5. "\\" - String Escape
========================

**Arity: One Character**

Creates a one character string containing the next character in the program.

Ex::

	==================================================
	\a
	==================================================
	Pprint("\n","a")
	==================================================
	a

9.6. "]" - One Element List
===========================

**Arity: 1**

Makes a list containing only one element.

Ex::

	==================================================
	]5
	==================================================
	Pprint("\n",[5])
	==================================================
	[5]

9.7. "," - Couple Constructor
=============================

**Arity: 2**

A couple is a tuple containing only two elements. This creates one containing the arguments passed to it. This is useful for ``A``, the double assignment operator.

Ex::

	==================================================
	,5T
	==================================================
	Pprint("\n",(5,T))
	==================================================
	(5, 10)

9.8. "a" - Append
=================

**Arity: 2**

Appends the second argument to the first arguement, a sequence.

Ex::

	==================================================
	aY5Y
	==================================================
	Y.append(5)
	Pprint("\n",Y)
	==================================================
	[5]

9.9. "c" - Chop
===============

*Arity: 2**

9.9.1. Seq a, Int b: Chop
-------------------------

Splits sequence ``a`` every ``b`` elements.

Ex::

	==================================================
	cG2
	==================================================
	Pprint("\n",chop(G,2))
	==================================================
	['ab', 'cd', 'ef', 'gh', 'ij', 'kl', 'mn', 'op', 'qr', 'st', 'uv', 'wx', 'yz']

9.9.2. Str a, Str b: String Split
---------------------------------

Splits string ``a`` by occurrences of string ``b``. Uses ``string.split()``. If ``b`` is ``None`` (default value) it splits by whitespace.

Ex::

	==================================================
	c"kjclkshfglasjfljdlakjaflkajflkajfalkjgaf"\a
	==================================================
	Pprint("\n",chop("kjclkshfglasjfljdlakjaflkajflkajfalkjgaf","a"))
	==================================================
	['kjclkshfgl', 'sjfljdl', 'kj', 'flk', 'jflk', 'jf', 'lkjg', 'f']

9.9.3. Num a, Num b: Float Division
-----------------------------------

Computes true division on the arguments. Does not truncate the result.

Ex::

	==================================================
	cT4
	==================================================
	Pprint("\n",chop(T,4))
	==================================================
	2.5

9.10. "e" - End
===============

**Arity: 1**

9.10.1. Seq a: End
------------------

Returns the last element of sequence ``a``.

Ex::

	==================================================
	e"abc"
	==================================================
	Pprint("\n",end("abc"))
	==================================================
	c

9.10.2. Num a: Modulus By Ten
-----------------------------

Returns ``a%10`` which is the remainder when ``a`` is divided by ``10``.

Ex::

	==================================================
	e25
	==================================================
	Pprint("\n",end(25))
	==================================================
	5

9.11. "h" - Head
================

**Arity: 1**

9.11.1. Seq a: Head
-------------------

Returns the first element of sequence ``a``.

Ex::

	==================================================
	h"abc"
	==================================================
	Pprint("\n",head("abc"))
	==================================================
	a

9.11.2. Num a: Increment
------------------------

Returns ``a+1``.

Ex::

	==================================================
	h5
	==================================================
	Pprint("\n",head(5))
	==================================================
	6

9.12. "j" - Join
================

**Arity: 2**

9.12.1. Str a, Seq b: Join
--------------------------

This works the same as the Python ``string.join()``. It takes sequence b and concatenates all of its elements, separated by string a.

Ex::

	==================================================
	jdUT
	==================================================
	Pprint("\n",join(d,urange(T)))
	==================================================
	0 1 2 3 4 5 6 7 8 9

9.12.2. Int a, Int b: Base Conversion
-------------------------------------

This takes the integer a, and converts it into base b. It however, outputs the result in a list of digits.

Ex::

	==================================================
	jT2
	==================================================
	Pprint("\n",join(T,2))
	==================================================
	[1, 0, 1, 0]

9.13. "l" - Length
==================

**Arity: 1**

9.13.1. Seq a: Length
---------------------

Returns the length of sequence a. Uses Python ``len()``.

Ex::

	==================================================
	lG
	==================================================
	Pprint("\n",Plen(G))
	==================================================
	26

9.13.2. Num a: Log Base 2
-------------------------

Calculates the logarithm in base two of a.

Ex::

	==================================================
	lT
	==================================================
	Pprint("\n",Plen(T))
	==================================================
	3.3219280948873626

9.14. "r" - Range
=================

**Arity: 2**

9.14.1. Int a, Int b: Range
---------------------------

Returns a list containing the integers over the range ``[a, b)``. Like Python, it is inclusive of ``a`` but not of ``b``

Ex::

	==================================================
	r5T
	==================================================
	Pprint("\n",Prange(5,T))
	==================================================
	[5, 6, 7, 8, 9]

9.14.2. Str a, Int b: String Processing
---------------------------------------

Pyth's Range function contains a lot of string processing functions. It processes the input string ``a`` in various ways depending on the option provided by integer ``b``.

9.14.2.1. Option 0: Lowercase
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Returns the string with all letters lower-cased. Uses ``str.lower()`` from Python.

Ex::

	==================================================
	r"HEEElllloooooooBYE"Z
	==================================================
	Pprint("\n",Prange("HEEElllloooooooBYE",Z))
	==================================================
	heeellllooooooobye

9.14.2.2. Option 1: Uppercase
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Returns the string with all letters upper-cased. Uses ``str.upper()`` from Python.

Ex::

	==================================================
	r"HEEElllloooooooBYE"1
	==================================================
	Pprint("\n",Prange("HEEElllloooooooBYE",1))
	==================================================
	HEEELLLLOOOOOOOBYE

9.14.2.3. Option 2: Swapcase
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Returns the string with all the cases switched (i.e. all upper-cased become lower-cased and vice versa). Uses ``str.swapcase()`` from Python.

Ex::

	==================================================
	r"HEEElllloooooooBYE"2
	==================================================
	Pprint("\n",Prange("HEEElllloooooooBYE",2))
	==================================================
	heeeLLLLOOOOOOObye

9.14.2.4. Option 3: Title Case
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Splits the string up by all occurrences of non-alphabetical characters and capitalizes the first letter of all tokens. Internally it is ``str.title()``.

Ex::

	==================================================
	r"the philosopher's stone"3
	==================================================
	Pprint("\n",Prange("the philosopher's stone",3))
	==================================================
	The Philosopher'S Stone

9.14.2.5. Option 4: Capitalize:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Returns the string so that the first letter of the string is capitalized and all others are lower-cased. Uses ``str.capitalize()``.

Ex::

	==================================================
	r"the Philosopher's stone"4
	==================================================
	Pprint("\n",Prange("the Philosopher's stone",4))
	==================================================
	The philosopher's stone

9.14.2.6. Option 5: Capwords
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is almost the same as Option # 3 in that it tokenizes and capitalizes the first letter of each token in the string. However, it does not capitalize by all non-alphabetical but only by spaces. Uses the ``capwords()`` function from the ``string``` module.

Ex::

	==================================================
	r"the philosopher's stone"5
	==================================================
	Pprint("\n",Prange("the philosopher's stone",5))
	==================================================
	The Philosopher's Stone

9.14.2.7. Option 6: Strip
^^^^^^^^^^^^^^^^^^^^^^^^^

This removes all whitespace from the beginning and end of the string. Note that it leaves all whitespace in the middle of the string untouched. Uses ``str.strip()``.

Ex::

	==================================================
	+r"          the philosopher's stone       "5G
	==================================================
	Pprint("\n",plus(Prange("          the philosopher's stone       ",5),G))
	==================================================
	The Philosopher's Stoneabcdefghijklmnopqrstuvwxyz

9.14.2.8. Option 7: Evaluate Tokens
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This tokenizes the string by whitespace, then evaluates each token into a Python object.

Ex::

	==================================================
	sr"1 2 3 4 5 6 7 8 9 10"7
	==================================================
	Pprint("\n",Psum(Prange("1 2 3 4 5 6 7 8 9 10",7)))
	==================================================
	55

9.15. "s" - Sum
===============

**Arity: 1**

9.15.1. Seq a: Sum
------------------

This sums the numbers in the sequence. The base case for an empty list is ``0``.

Ex::

	==================================================
	sUT
	==================================================
	Pprint("\n",Psum(urange(T)))
	==================================================
	45

9.15.2. Str a: Int
------------------

This converts string ``a`` into an integer. Uses Python's ``int()`` built-in.

Ex::

	==================================================
	s"123
	==================================================
	Pprint("\n",Psum("123"))
	==================================================
	123

9.16. "t" - Tail
================

**Arity: 1**

9.16.1. Seq a: Tail
-------------------

Returns all but the first element of the sequence. Equivelant to the slice ``a[1:]``.

Ex::

	==================================================
	tG
	==================================================
	Pprint("\n",tail(G))
	==================================================
	bcdefghijklmnopqrstuvwxyz

9.16.2. Num a: Decrement
------------------------

Returns ``a-1``.

Ex::

	==================================================
	tT
	==================================================
	Pprint("\n",tail(T))
	==================================================
	9

9.17. "x" - Index
=================

**Arity: 2**

9.17.1. Seq a, Element b: Index Of
----------------------------------

Returns the position of the first occurrence of element b within sequence a. Returns ``-1`` if it is not found.

Ex::

	==================================================
	xG\f
	==================================================
	Pprint("\n",index(G,"f"))
	==================================================
	5

9.18.1. Int a, Int b: XOR
-------------------------

Computes the `bitwise XOR <http://en.wikipedia.org/wiki/Bitwise_operation#XOR>`_ of ``a`` and ``b``. Same as Python ``a^b``.

Ex::

	==================================================
	xT2
	==================================================
	Pprint("\n",index(T,2))
	==================================================
	8

9.18. "y" - Powerset
====================

**Arity: 1**

9.18.1. Seq a: Powerset
-----------------------

Returns the `powerset <http://en.wikipedia.org/wiki/Power_set>`_ of sequence a. The powerset is the set of all possible sets using the elements of sequence a.

Ex::

	==================================================
	yU3
	==================================================
	Pprint("\n",subsets(urange(3)))
	==================================================
	[[], [0], [1], [2], [0, 1], [0, 2], [1, 2], [0, 1, 2]]

9.18.2. Num a: Double
---------------------

Returns ``a*2``.

Ex::

	==================================================
	yT
	==================================================
	Pprint("\n",subsets(T))
	==================================================
	20

9.19. "S" - Sorted
==================

**Arity: 1**

Returns the input, except sorted. The same as python ``sorted()``.

Ex::

	==================================================
	S"asjdasljls"
	==================================================
	Pprint("\n",Psorted("asjdasljls"))
	==================================================
	aadjjllsss

9.20. "U" - Unary Range
=======================

**Arity: 1**

9.20.1. Int a: Unary Range
--------------------------

Returns all the integers in the range ``[0, a)``.It is the same as ``r`` with first parameter being ``0``.

Ex::

	==================================================
	UT
	==================================================
	Pprint("\n",urange(T))
	==================================================
	[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

9.20.2. Len 2 Tuple a: Splat Range
----------------------------------

This "splats" the tuple on to the range function. This means that it does the range ``[a[0], a[1])``.

Ex::

	==================================================
	U,5T
	==================================================
	Pprint("\n",urange((5,T)))
	==================================================
	[5, 6, 7, 8, 9]

9.20.3. Seq a: Len Unary Range
------------------------------

Does the same as normal unary range, except it uses ``len(a)`` as the parameter.

Ex::

	==================================================
	UG
	==================================================
	Pprint("\n",urange(G))
	==================================================
	[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

9.21. "X" - Update Mutable
==========================

**Arity: 3**

9.21.2. Seq a, Index b, Value c: Update Mutable
----------------------------------------------

This updates the mutable sequence (list or dict) by assigning the value at index b to value c. This is equivalent to the Python ``a[b]=c``. This both updates the mutable and returns the updated.

Ex::

	==================================================
	XUT5Z
	==================================================
	Pprint("\n",assign_at(urange(T),5,Z))
	==================================================
	[0, 1, 2, 3, 4, 0, 6, 7, 8, 9]