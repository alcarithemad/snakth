(class foo (object)
    (def bar (self)
        (return "bar")
    )
    (def baz (self)
        (return (+ (self.bar) "baz"))
    )
)
(print ((foo).baz))