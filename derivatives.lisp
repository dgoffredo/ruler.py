
; Derivatives of the core arithmetic operators
(defrule (d (+ :a :b)) (+ (d :a) (d :b)))
(defrule (d (* :a :b)) (+ (* :a (d :b)) (* :b (d :a))))

; If you want to differentiate arbitrary powers (not just integer exponents),
; then you need logarithms. But then if you have logarithms you can
; differentiate those, so then you need the multiplicative inverse, but then
; to differentiate those you need the additive inverse. At that point it's
; convenient to define the behavior of 1 and 0. So you end up having a bunch
; of math. Finally, you can define the general power function in terms of
; the natural exponential and logarithm.
(defrule (d (exp :x)) (* (exp :x) (d :x)))
(defrule (d (log :x)) (* (inv :x) (d :x)))
(defrule (d (inv :x)) (* (neg (inv (* :x :x))) (d :x))) ; This one is cool.
(defrule (d (neg :x)) (neg (d :x)))

; Generic power function
(defrule (^ :a :b) (exp (* (log :a) :b)))

; Some simplifying rules
(defrule (inv (inv :x)) :x)
(defrule (neg (neg :x)) :x)

; 1 and 0
(defrule (* 1 :x) :x)
(defrule (* :x 1) :x)
(defrule (inv 1) 1)
(defrule (+ 0 :x) :x)
(defrule (+ :x 0) :x)
(defrule (* 0 :x) 0)
(defrule (* :x 0) 0)
(defrule (neg 0) 0)
(defrule (+ :x (neg :x)) 0)
(defrule (+ (neg :x) :x) 0)
(defrule (exp 0) 1)
(defrule (log 1) 0)
(defrule (d 1) 0)
(defrule (d 0) 0)
