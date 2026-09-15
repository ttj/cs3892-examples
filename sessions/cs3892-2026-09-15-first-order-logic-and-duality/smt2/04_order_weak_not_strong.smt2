; EXPECT: sat
; Slide 21 -- the direction that does NOT hold.
;
; Here Sess(u,s) is true exactly when s = u: every user has their own session
; and no two users share one. So:
;
;   forall u. exists s. Sess(u,s)   holds  -- take s = u
;   exists s. forall u. Sess(u,s)   fails  -- no single s equals every u
;
; `sat` is the proof that the two orderings are different specifications. In a
; security property the difference between them is usually the vulnerability.

(define-fun Sess ((u Int) (s Int)) Bool (= u s))

(assert (forall ((u Int)) (exists ((s Int)) (Sess u s))))
(assert (not (exists ((s Int)) (forall ((u Int)) (Sess u s)))))

(check-sat)
