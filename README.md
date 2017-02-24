# ruler.py
Mechanical symbolic transformations with lisp syntax

# What

    $ python3 ruler.py
    ruler> (defrule (d (+ :a :b)) (+ (d :a) (d :b)))
    (defrule (d (+ :a :b)) (+ (d :a) (d :b)))

    ruler> (defrule (d (* :a :b)) (+ (* :a (d :b)) (* :b (d :a))))
    (defrule (d (* :a :b)) (+ (* :a (d :b)) (* :b (d :a))))

    ruler> (d (+ x (* a b)))
    (+ (d x) (+ (* a (d b)) (* b (d a))))

    ruler>

# Why
Because!

# More

    $ cat derivatives.lisp - | python3 ruler.py
    ...
    ruler> (d (inv (+ 1 (exp (neg (* x x))))))
    (* (neg (inv (* (+ 1 (exp (neg (* x x)))) (+ 1 (exp (neg (* x x))))))) (+ (d 1) (* (exp (neg (* x x))) (neg (+ (* x (d x)) (* x (d x)))))))

