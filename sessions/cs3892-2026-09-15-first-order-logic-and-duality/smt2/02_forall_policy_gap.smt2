; EXPECT: sat
; Slide 25 -- the same policy, with 18 changed to 6.
;
; `sat` here is not the solver failing. The rule only ever said what happens
; at twelve months or more; it said nothing at all about six. So a user with
; six months who is NOT approved is perfectly consistent with the policy.
;
; The solver has just found a hole in the specification. That is the most
; useful thing an unsatisfiability checker does for you: when you expected a
; proof and got a model instead, read the model.

(declare-fun months (Int) Int)
(declare-fun approved (Int) Bool)

(assert (forall ((u Int))
  (=> (>= (months u) 12) (approved u))))

(declare-const bob Int)
(assert (= (months bob) 6))
(assert (not (approved bob)))

(check-sat)
(get-model)
