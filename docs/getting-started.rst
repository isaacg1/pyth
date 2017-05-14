1. Getting Started
******************

Pyth is a golfing language based on Python (hence the name) created by `Programming Puzzles and Code Golf <http://codegolf.stackexchange.com>`_ (PPCG) user `Isaacg <http://codegolf.stackexchange.com/users/20080/isaacg>`_. Unlike most golfing languages, Pyth is fully procedural. Since Pyth is quite young, its features are constantly changing, and this document might be out of date for a few functions (Just check the source). Pyth is licensed under the `MIT license <http://opensource.org/licenses/MIT>`_.

1.1. How to Start Programming in Pyth
=====================================
You have a few options when it comes to running Pyth. You could install it on your machine by cloning `the repository <https://github.com/isaacg1/pyth>` then adding this alias to your .bashrc::

	alias pyth="python3 <path to pyth>/pyth.py"

(Windows users, you'll have to use the PATH and call ``pyth.py``)

But the method we will be using in the tutorial, and the suggested one, is to use the online interpreter at http://pyth.herokuapp.com. This provides a programming environment with places in which to put code and input (and a handy function cheat-sheet!). The code is executed on the server and sent back to the webpage. The examples won't be too different if you decide to install the interpreter yourself. Installing the interpreter, however, will become necessary, when we start conducting "unsafe" operations which allow for arbitrary execution of code.

1.2. Hello World!
=================

A customary start to programming tutorials is the "Hello World Program" which consists of printing out the text "Hello World!".  Since Pyth *is* a golfing language, let's golf it! In the process, we will demonstrate some key features of Pyth. So without further ado, here is our first program::

	"Hello World!

Type this into the code textbox, leave the input box empty, click the run button. The results (in the output box) should look something like this::

	Hello World!

Well, that went pretty much as expected, but if you have any experience with other programming languages, you'll notice a few interesting things about the program.

#. Printing is implicit (Just name a value or identifier and it will be printed).
#. Quotes are automatically closed at the end of the program.

These features are obviously beneficially for reducing the length of your programs. Another thing you should know early on if you decide to go experimenting on your own is that programs in Pyth are typically only one line long. Statement separation is typically achieved through semicolons: ``;``.
