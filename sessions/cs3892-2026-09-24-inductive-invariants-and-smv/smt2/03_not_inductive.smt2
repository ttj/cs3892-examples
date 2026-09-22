; EXPECT: sat
; Session 9. The SAME consecution query for a machine where it FAILS.
;
;   I(x) = (x = 0),  T(x,x') = (x' = x + 2),  P(x) = (x /= 5)
;
; P is a true invariant -- every reachable x is even, and 5 is odd. But
; consecution quantifies over every x satisfying P, reachable or not, and
; x = 3 satisfies P while stepping straight onto 5.
;
; `sat` here is a COUNTEREXAMPLE TO INDUCTION (a CTI), not a bug in the
; system. Ask for the model and you get x = 3.

(set-logic QF_LIA)

(declare-const x  Int)
(declare-const xp Int)

(assert (not (= x 5)))        ; P(x)
(assert (= xp (+ x 2)))       ; T(x,x')
(assert (= xp 5))             ; not P(x')

(check-sat)
(get-model)
