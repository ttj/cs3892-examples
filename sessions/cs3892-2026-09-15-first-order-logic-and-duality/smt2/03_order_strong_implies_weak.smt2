; EXPECT: unsat
; Slide 21 -- "Order matters, and it changes the meaning" (the easy direction)
;
;   exists s. forall u. Sess(u,s)     "one session serves everyone"
;   forall u. exists s. Sess(u,s)     "everyone has a session, maybe their own"
;
; The first implies the second. Assert the first and the NEGATION of the second;
; unsat says no counterexample exists, so the implication is valid.

(declare-sort U 0)   ; users
(declare-sort S 0)   ; sessions
(declare-fun Sess (U S) Bool)

(assert (exists ((s S)) (forall ((u U)) (Sess u s))))
(assert (not (forall ((u U)) (exists ((s S)) (Sess u s)))))

(check-sat)
