; EXPECT: unsat
; Slide 23 -- "The identity every verifier is built on"
;
;     phi is valid  <=>  (not phi) is unsatisfiable
;
; A solver has no "is it valid?" button. To show p OR (not p) is a tautology
; you assert its NEGATION and watch the solver fail to satisfy it. Every
; verifier in this course is built on this one move.

(declare-const p Bool)
(assert (not (or p (not p))))
(check-sat)
