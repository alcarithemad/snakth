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
(foo ::(dict (zip "abcd" "1234"))); and kwargs
(foo :"1234" ::(dict (zip "cdef" "1234"))); varargs and kwargs together
(def bar (x) (return (+ "..." x)))
(print "I have" (bar "returned!"))
