; EXPECT: unsat
; Slide 22 -- "Where every counterexample comes from"
;
;   not (forall x. P(x))   ===   exists x. not P(x)
;
; De Morgan, one level up: a forall is a conjunction over the domain and an
; exists is a disjunction, so this is the same law proved on the board on
; September 10. Asserting that the two sides DIFFER is unsat, which is the
; machine-checked version of that proof.
;
; This equivalence is the entire verification loop. "For every reachable state,
; nothing bad" negates into "there exists a reachable state where something
; bad" -- and that is the query the solver is actually given.

(declare-fun P (Int) Bool)

(assert (not (= (not (forall ((x Int)) (P x)))
                (exists ((x Int)) (not (P x))))))

(check-sat)
