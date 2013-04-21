snakth
======

A sexp -> python compiler.

Wait, what?
=======

This compiles s-expressions (think lisp, parentheses everywhere) to Python by way of the normal Python AST. It's all very pre-pre-alpha, but you can do quite a bit with it already:

```
; is a comment
(import re); from re import match as regex
(if (re.match "^\\d{3}-\\d{4}$" (raw_input "phone number? "))
    (print "that's probably a phone number")
    (print "that doesn't look like a phone number")
)

(print ("we also support subscripts and dotted names"[3].lower))

; you can, of course, define functions
(def foo (a b:1 *c **d) (print a b c d))

; ...and call them
(foo 0); using default args
(foo :(list "asdf")); and varargs
(foo ::(dict (zip (list "abcd") (list "1234")))); and kwargs
(foo :(list "1234") ::(dict (zip (list "cdef") (list "1234")))); varargs and kwargs together
(def bar (x) (return x))
(print "I have" (bar "returned!"))
```

There's even a version of lisp.py (the main interpreter script) written in this form, as lisp.lisp!

TODO:
* more options for literals (floats, hexadecimal/octal/binary numbers, real string escapes)
* loop constructs (for, while)
* yield
* classes (easier than it sounds)
* probably other things

Why 'snakth'?
=======

It's how one might say 'snake' if one had a very bad lisp.
