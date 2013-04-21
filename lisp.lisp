(import lexer Lexer)
(import parser Parser)
(import sys argv)

(if (= __name__ "__main__")
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
)