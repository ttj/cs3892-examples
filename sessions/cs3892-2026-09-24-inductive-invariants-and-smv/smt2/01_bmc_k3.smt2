; EXPECT: unsat
; Session 9. The BMC query for the CANONICAL counter at k = 3, written out
; by hand so the shape is visible with nothing hidden behind notation.
;
;   I(x)     x = 0
;   T(x,x')  (x < 10 and x' = x+1) or (x >= 10 and x' = 0)
;   P(x)     x <= 10
;
; One variable per step; the transition relation copied k times; the NEGATED
; property asserted somewhere along the path. `unsat` = no counterexample of
; length <= 3. It is not a proof of safety -- see 02_induction.smt2.

(set-logic QF_LIA)

(declare-const x0 Int)
(declare-const x1 Int)
(declare-const x2 Int)
(declare-const x3 Int)

; I(x0)
(assert (= x0 0))

; T(x0,x1) and T(x1,x2) and T(x2,x3)
(assert (or (and (< x0 10) (= x1 (+ x0 1))) (and (>= x0 10) (= x1 0))))
(assert (or (and (< x1 10) (= x2 (+ x1 1))) (and (>= x1 10) (= x2 0))))
(assert (or (and (< x2 10) (= x3 (+ x2 1))) (and (>= x2 10) (= x3 0))))

; the negated property, somewhere on the path
(assert (or (> x0 10) (> x1 10) (> x2 10) (> x3 10)))

(check-sat)
