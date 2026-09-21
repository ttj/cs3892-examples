; EXPECT: unsat
; Session 8, demo 1. The boolean skeleton `p and q` is satisfiable; the
; formula is not. The theory solver for linear integer arithmetic is the
; only thing that knows that, and DPLL(T) is the loop that asks it.

(set-logic QF_LIA)
(declare-const x Int)

(assert (> x 5))
(assert (< x 3))

(check-sat)
