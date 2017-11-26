Pyth
====

Pyth, an extremely concise language.

[Try it here.](https://pyth.herokuapp.com/)

[Tutorial here.](https://pyth.readthedocs.org/en/latest/)

----

## Recent changes:

### 11/26/17

* `=` and `~` now allow an implicit `Q` if they are not followed by any variables for the rest of the program.
  * For instance, in the program `mQ=h`, the `=` assigns the result of `h`, which expands to `hQ` to `Q`. Thus, with an input of `2`, the output is `[3, 3, 3]`.

### 8/20/17

* `J` and `K` now define assignment expressions until an assignment expression is complete, since the associated variables are not defined until that point. 
  * For instance, in the program `J+J4*J3J`, the first `J` defines an assignment expression. `+` is part of that expression, `J` is part of that expression and defines another assignment expression. That inner assignment gives `J` the value `4`. Now, J is defined, and so it is treated as a variable in the expression `*J3`. Then, the final `J` is an expression of its own, and prints out `J`'s new value at this point, 16. 
