; EXPECT: unsat
; Slide 25 -- "A policy that covers users you have never seen"
;
; One assertion covers every user at once. `bob` is declared AFTER the rule and
; the rule still binds him -- which the 1000 propositional clauses on slide 15
; could not do, because they had to name every user in advance.
;
; unsat = no such user can exist = the policy is enforced. Z3 never enumerates
; the domain; it instantiates the quantifier with the one term it needs.

(declare-fun months (Int) Int)
(declare-fun approved (Int) Bool)

; the rule: twelve months of service or more means approved
(assert (forall ((u Int))
  (=> (>= (months u) 12) (approved u))))

; could SOME user with 18 months be unapproved?
(declare-const bob Int)
(assert (= (months bob) 18))
(assert (not (approved bob)))

(check-sat)
