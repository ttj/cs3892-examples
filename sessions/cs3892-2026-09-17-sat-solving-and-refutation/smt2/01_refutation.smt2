; EXPECT: unsat
; Slide 24 -- "Proof by refutation, on the board and in the solver"
;
; The contrapositive law proved by hand on September 10:
;
;     (not q -> not p)  ===  (p -> q)
;
; To prove it, do not try to show it is true everywhere. Assert that it is
; FALSE -- that the two sides differ -- and ask whether that is satisfiable.
; `unsat` means no interpretation makes them differ, which is exactly what
; "valid" means. Every tool in this course proves things this way.

(declare-const p Bool)
(declare-const q Bool)

(assert (not (= (=> (not q) (not p))
                (=> p q))))

(check-sat)
