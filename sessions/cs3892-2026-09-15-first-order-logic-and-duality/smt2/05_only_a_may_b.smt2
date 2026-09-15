; EXPECT: sat
; Slide 23 -- "Only users with an active session may read a document."
;
;   correct:   forall u,d. Reads(u,d) => Active(u)
;   reversed:  forall u,d. Active(u) => Reads(u,d)
;
; These are not the same claim, and `sat` proves it: there is a world where the
; correct reading holds and the reversed one fails. (Take a world where nobody
; reads anything and somebody is active.)
;
; "Only A may B" becomes B => A, never A => B. That single reversal is the most
; common specification bug there is -- and the solver will happily prove the
; reversed version for you without ever mentioning that you asked the wrong
; question.

(declare-fun Reads (Int Int) Bool)
(declare-fun Active (Int) Bool)

(assert      (forall ((u Int) (d Int)) (=> (Reads u d) (Active u))))
(assert (not (forall ((u Int) (d Int)) (=> (Active u) (Reads u d)))))

(check-sat)
