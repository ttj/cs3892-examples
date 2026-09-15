; EXPECT: unsat
; Slide 32 -- the same encoding, one edge richer.
;
; Four regions, every one adjacent to every other, three colours. There is no
; legal colouring, and `unsat` is a PROOF of that -- not "I looked and did not
; find one". Four mutually adjacent regions need four colours; three pigeons
; do not fit in four holes the other way round.
;
; In the language of today: the set of legal colourings is EMPTY. That is what
; unsat means, and it is why unsat is the answer you want when you are trying
; to show something cannot happen.

(declare-const r1 Int) (declare-const r2 Int)
(declare-const r3 Int) (declare-const r4 Int)

(assert (and (<= 1 r1) (<= r1 3)))
(assert (and (<= 1 r2) (<= r2 3)))
(assert (and (<= 1 r3) (<= r3 3)))
(assert (and (<= 1 r4) (<= r4 3)))

; every pair adjacent
(assert (not (= r1 r2))) (assert (not (= r1 r3))) (assert (not (= r1 r4)))
(assert (not (= r2 r3))) (assert (not (= r2 r4))) (assert (not (= r3 r4)))

(check-sat)
