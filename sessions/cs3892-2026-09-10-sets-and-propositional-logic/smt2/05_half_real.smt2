; EXPECT: sat
; Slide 30 -- "Demo 3" (second half)
;
; The SAME formula over the reals. One word changed; opposite answer. This is
; why "is it satisfiable?" is not well formed until you say satisfiable in what.

(declare-const x Real)
(assert (= (* 2 x) 1))
(check-sat)
(get-model)
