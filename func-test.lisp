(def foo (a b:1 *c **d) (print a b c d))
(foo 0); show off default args
(foo :(list "asdf")); show off varargs
(foo ::(dict (zip (list "abcd") (list "1234")))); kwargs
(foo :(list "1234") ::(dict (zip (list "cdef") (list "1234")))); varargs and kwargs together
(def bar (x) (return x))
(print "I have" (bar "returned!"))
