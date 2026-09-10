; EXPECT: unsat
; Slide 30 -- "Demo 3: the theory is not decoration" (first half)
;
; 2x = 1 has no solution in the integers.

(declare-const x Int)
(assert (= (* 2 x) 1))
(check-sat)
