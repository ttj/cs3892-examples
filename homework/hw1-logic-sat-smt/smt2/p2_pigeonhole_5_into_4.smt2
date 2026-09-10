; EXPECT: unsat
; HW1 part 2 -- the pigeonhole principle, written out by hand.
;
; Five pigeons, four holes. Every pigeon is in some hole; no hole holds two.
; The solver proves this is impossible -- and note how the encoding GROWS: the
; "no hole holds two" clauses are quadratic in the number of pigeons. That is
; the wall part 2 asks you to find, and it is a property of the encoding, not
; of Z3.

(declare-const p0h0 Bool) (declare-const p0h1 Bool) (declare-const p0h2 Bool) (declare-const p0h3 Bool)
(declare-const p1h0 Bool) (declare-const p1h1 Bool) (declare-const p1h2 Bool) (declare-const p1h3 Bool)
(declare-const p2h0 Bool) (declare-const p2h1 Bool) (declare-const p2h2 Bool) (declare-const p2h3 Bool)
(declare-const p3h0 Bool) (declare-const p3h1 Bool) (declare-const p3h2 Bool) (declare-const p3h3 Bool)
(declare-const p4h0 Bool) (declare-const p4h1 Bool) (declare-const p4h2 Bool) (declare-const p4h3 Bool)

; every pigeon is in at least one hole
(assert (or p0h0 p0h1 p0h2 p0h3))
(assert (or p1h0 p1h1 p1h2 p1h3))
(assert (or p2h0 p2h1 p2h2 p2h3))
(assert (or p3h0 p3h1 p3h2 p3h3))
(assert (or p4h0 p4h1 p4h2 p4h3))

; no hole holds two pigeons
(assert (not (and p0h0 p1h0))) (assert (not (and p0h0 p2h0))) (assert (not (and p0h0 p3h0))) (assert (not (and p0h0 p4h0)))
(assert (not (and p1h0 p2h0))) (assert (not (and p1h0 p3h0))) (assert (not (and p1h0 p4h0)))
(assert (not (and p2h0 p3h0))) (assert (not (and p2h0 p4h0))) (assert (not (and p3h0 p4h0)))
(assert (not (and p0h1 p1h1))) (assert (not (and p0h1 p2h1))) (assert (not (and p0h1 p3h1))) (assert (not (and p0h1 p4h1)))
(assert (not (and p1h1 p2h1))) (assert (not (and p1h1 p3h1))) (assert (not (and p1h1 p4h1)))
(assert (not (and p2h1 p3h1))) (assert (not (and p2h1 p4h1))) (assert (not (and p3h1 p4h1)))
(assert (not (and p0h2 p1h2))) (assert (not (and p0h2 p2h2))) (assert (not (and p0h2 p3h2))) (assert (not (and p0h2 p4h2)))
(assert (not (and p1h2 p2h2))) (assert (not (and p1h2 p3h2))) (assert (not (and p1h2 p4h2)))
(assert (not (and p2h2 p3h2))) (assert (not (and p2h2 p4h2))) (assert (not (and p3h2 p4h2)))
(assert (not (and p0h3 p1h3))) (assert (not (and p0h3 p2h3))) (assert (not (and p0h3 p3h3))) (assert (not (and p0h3 p4h3)))
(assert (not (and p1h3 p2h3))) (assert (not (and p1h3 p3h3))) (assert (not (and p1h3 p4h3)))
(assert (not (and p2h3 p3h3))) (assert (not (and p2h3 p4h3))) (assert (not (and p3h3 p4h3)))

(check-sat)
