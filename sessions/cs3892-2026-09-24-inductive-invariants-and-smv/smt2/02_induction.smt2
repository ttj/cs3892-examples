; EXPECT: unsat
; Session 9. CONSECUTION for the canonical counter -- the query that settles
; every k at once, and the one with no k in it anywhere.
;
;   Inv(x) and T(x,x')  =>  Inv(x')        with Inv = P = (x <= 10)
;
; A validity question becomes an unsatisfiability question, exactly as in
; session 7: assert the NEGATION and hope for `unsat`.
;
; Note there are only TWO variables here, not k+1. That is the whole saving:
; the formula does not grow with the length of the run, because it never
; mentions the length of the run.

(set-logic QF_LIA)

(declare-const x  Int)
(declare-const xp Int)

; assert the negation of  (Inv(x) and T(x,x')) => Inv(x')
(assert (<= x 10))                                                  ; Inv(x)
(assert (or (and (< x 10) (= xp (+ x 1))) (and (>= x 10) (= xp 0)))); T(x,x')
(assert (not (<= xp 10)))                                           ; not Inv(x')

(check-sat)
