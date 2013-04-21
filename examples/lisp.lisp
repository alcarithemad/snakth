(import lexer Lexer)
(import parser Parser)
(import sys argv)

(if (= __name__ "__main__")
    (if (>= (len argv) 3)
    (exec
        (compile
            (
                (Parser (Lexer (
                                (file argv[2] "rb").read
                            )
                        )
                ).run
            )
            "func-test.lisp"
            "exec"
        )
    )
    (print "usage is lisp.lisp <file>")
    )
)
