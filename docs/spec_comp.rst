8. The Language Specification - Comparisons
*******************************************

This section contains a list of comparison operators. They all take two arguments and return a boolean value depending on the relationship between the two arguments.

8.1. "<" - Is Less Than
=======================

**Arity: 2**

8.1.1. Any a, Same Type b: Less Than
------------------------------------

If a and b are of the same type, checks if ``a`` is less than ``b`` by whatever way that type is compared (e.g. Numbers by size, strings lexicographically).

Ex::

	==================================================
	<5T<T5
	==================================================
	Pprint("\n",lt(5,T))
	Pprint("\n",lt(T,5))
	==================================================
	True
	False

8.1.2. Seq a, Int b: Slice Till
-------------------------------

Takes a slice of sequence ``a`` until index ``b``. This is equivalent to the Python statement ``a[:b]``. The slice is inclusive of the element at index ``b``

Ex::

	==================================================
	>"abcdefgh"5
	==================================================
	Pprint("\n",gt("abcdefgh",5))
	==================================================
	fgh

8.1.3. Set a, Set b: Is Subset
------------------------------

Checks if set ``a`` is a subset of set ``b``. This means that it checks if set ``b`` contains all the elements of set ``a``.

Ex::

	==================================================
	<{[1 2){[1 2 3)
	==================================================
	Pprint("\n",lt(Pset(Plist(1,(2))),Pset(Plist(1,(2),(3)))))
	==================================================
	True

8.2. "q" - Is Equal To
======================

**Arity: 2**

This checks if the two values are equal to each other. This is the same as the Python ``==``.

Ex::

	==================================================
	qT5qTT
	==================================================
	Pprint("\n",equal(T,5))
	Pprint("\n",equal(T,T))
	==================================================
	False
	True

8.3. ">" - Is Greater Than
==========================

**Arity: 2**

8.3.1 Any a, Same Type b: Greater Than
--------------------------------------

This checks if ``a`` is greater than ``b``. Uses the same type of comparisons as ``<``

Ex::

	==================================================
	>5T>T5
	==================================================
	Pprint("\n",gt(5,T))
	Pprint("\n",gt(T,5))
	==================================================
	False
	True

8.3.2 Seq a, Int b: Slice From
------------------------------

This takes a slice of sequence ``a`` from index ``b`` onwards till the end. This is equivalent to the Python ``a[b:]``. The slice is not inclusive of the element at index ``b``.

Ex::

	<"abcdefgh"5
	==================================================
	Pprint("\n",lt("abcdefgh",5))
	==================================================
	abcde

8.3.3. Set a, Set b: Is Superset
--------------------------------

Checks is set ``a`` is a superset of set ``b``. This means that it checks if set ``a`` contains all the elements of set ``b``. This does not return True if the two sets are equal.

Ex::

	==================================================
	>{[1 2 3){[1 2)
	==================================================
	Pprint("\n",gt(Pset(Plist(1,(2),(3))),Pset(Plist(1,(2)))))
	==================================================
	True

8.4. "n" - Not Equal To
=======================

**Arity: 2**

Checks if the two elements are not equal to each other. This is equivalent to Python's "!=".

Ex::

	==================================================
	nT5nTT
	==================================================
	Pprint("\n",ne(T,5))
	Pprint("\n",ne(T,T))
	==================================================
	True
	False

8.5. "g" - Is Greater Than or Equal To
======================================

**Arity: 2**

8.5.1. Any a, Same Type b: Greater Than or Equal To
---------------------------------------------------

Checks if ``a`` is greater than or equal to ``b``.

Ex::

	==================================================
	gT5gTTg5T
	==================================================
	Pprint("\n",gte(T,5))
	Pprint("\n",gte(T,T))
	Pprint("\n",gte(5,T))
	==================================================
	True
	True
	False

8.5.2. Set a, Set b: Superset or Equal
--------------------------------------

Checks if set ``a`` is a superset of set ``b`` or equal to set ``b``.

Ex::

	==================================================
	g{[1 2 3){[2 3)g{[1 2 3){[1 2 3)
	==================================================
	Pprint("\n",gte(Pset(Plist(1,(2),(3))),Pset(Plist(2,(3)))))
	Pprint("\n",gte(Pset(Plist(1,(2),(3))),Pset(Plist(1,(2),(3)))))
	==================================================
	True
	True

8.6. "}" - Contains
===================

**Arity: 2**

Checks if the second argument, a sequence, contains the first argument. Is equivalent to the Python ``in`` operator. 

Ex::

	==================================================
	}\a"abc"
	==================================================
	Pprint("\n",("a" in "abc"))
	==================================================
	True