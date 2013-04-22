snakth
======

A sexp -> python compiler.

Wait, what?
=======

This compiles s-expressions (think lisp, parentheses everywhere) to Python by way of the normal Python AST. It's all very pre-pre-alpha, but you can do quite a bit with it already!

Check out doc/basics for a decent example.

How do I run it?
=======

`python snakth/snakth.py` will do that for you

You can also (mostly) transparently import code written this way:

```
import snakth
snakth.install_import_hook()

import <some module written in snakth>
```

Why 'snakth'?
=======

It's how one might say 'snake' if one had a very bad lisp.

TODO
=======

* more options for literals (floats, hexadecimal/octal/binary numbers)
* loop constructs (for, while)
* yield
* probably lots of other things
