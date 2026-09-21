; EXPECT: sat
; Session 8, demo 2, written out by hand at k = 4 so the SHAPE is visible.
;
; The thermostat: t starts at 20, each step adds +3 or -1, and the property
; is t < 30. Asserting the NEGATION -- some state has t >= 30 -- turns
; "is it safe?" into "is this satisfiable?", and the model is the trace.
;
; Note there is no loop and no recursion here. Unrolling is the whole trick:
; one variable per step, the transition relation written down k times.

(set-logic QF_LIA)

(declare-const t0 Int)
(declare-const t1 Int)
(declare-const t2 Int)
(declare-const t3 Int)
(declare-const t4 Int)

; initial state
(assert (= t0 20))

; the transition relation, four times
(assert (or (= t1 (+ t0 3)) (= t1 (- t0 1))))
(assert (or (= t2 (+ t1 3)) (= t2 (- t1 1))))
(assert (or (= t3 (+ t2 3)) (= t3 (- t2 1))))
(assert (or (= t4 (+ t3 3)) (= t4 (- t3 1))))

; the negated property: a bad state appears somewhere on the path
(assert (or (>= t0 30) (>= t1 30) (>= t2 30) (>= t3 30) (>= t4 30)))

(check-sat)
(get-model)
