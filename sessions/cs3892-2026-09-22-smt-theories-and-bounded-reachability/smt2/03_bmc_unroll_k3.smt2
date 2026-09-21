; EXPECT: unsat
; The same thermostat one step shorter -- and this is the slide that matters.
;
; `unsat` here does NOT mean the thermostat is safe. It means no counterexample
; exists WITHIN THREE STEPS. The bug is at step four (see 02_bmc_unroll_k4).
; Bounded means bounded: every verdict a bounded model checker gives you is
; relative to its bound, and a shallow bound reports "no bug found" in exactly
; the same words a correct system would.

(set-logic QF_LIA)

(declare-const t0 Int)
(declare-const t1 Int)
(declare-const t2 Int)
(declare-const t3 Int)

(assert (= t0 20))
(assert (or (= t1 (+ t0 3)) (= t1 (- t0 1))))
(assert (or (= t2 (+ t1 3)) (= t2 (- t1 1))))
(assert (or (= t3 (+ t2 3)) (= t3 (- t2 1))))

(assert (or (>= t0 30) (>= t1 30) (>= t2 30) (>= t3 30)))

(check-sat)
