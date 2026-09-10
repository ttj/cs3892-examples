; EXPECT: sat
; Slide 29, second half -- change 11 to 12 and the answer flips.
;
; A `sat` answer comes with a model: the world in which the claim holds. That
; model is as useful as the counterexample an `unsat` proof denies you.

(declare-const months Int)
(declare-const u Bool)
(declare-const c Bool)
(declare-const L Bool)

(assert (= L (and (>= months 12) u (not c))))
(assert (>= months 12))
(assert L)

(check-sat)
(get-model)
