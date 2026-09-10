; EXPECT: unsat
; Slide 27 -- "The policy, encoded"
;
; An employee may take extended leave if they have been employed at least
; twelve months and have unused leave remaining. Contractors are never eligible.
;
; The model has told a contractor with eleven months' service that they are
; eligible. Is that consistent with the policy? Everything here is a plain
; boolean: the solver is doing propositional reasoning and nothing more.

(declare-const e Bool)   ; employed 12 months or more
(declare-const u Bool)   ; unused leave remains
(declare-const c Bool)   ; is a contractor
(declare-const L Bool)   ; eligible

(assert (= L (and e u (not c))))       ; the policy
(assert c) (assert (not e)) (assert L) ; the claim

(check-sat)
