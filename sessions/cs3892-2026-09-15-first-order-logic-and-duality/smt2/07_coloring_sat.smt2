; EXPECT: sat
; Slide 32 -- "Encode a problem, ask for a witness"
;
; Five regions in a ring, each adjacent to the next. Three colours.
; The formula says nothing about HOW to colour it -- only what a legal
; colouring is. The solver finds one.
;
; This is the shape of most of HW1: describe the legal states, then ask.

(declare-const r1 Int) (declare-const r2 Int) (declare-const r3 Int)
(declare-const r4 Int) (declare-const r5 Int)

; three colours, named 1 2 3
(assert (and (<= 1 r1) (<= r1 3)))
(assert (and (<= 1 r2) (<= r2 3)))
(assert (and (<= 1 r3) (<= r3 3)))
(assert (and (<= 1 r4) (<= r4 3)))
(assert (and (<= 1 r5) (<= r5 3)))

; neighbours differ, around the ring
(assert (not (= r1 r2))) (assert (not (= r2 r3))) (assert (not (= r3 r4)))
(assert (not (= r4 r5))) (assert (not (= r5 r1)))

(check-sat)
(get-model)
