; EXPECT: sat
; HW1 part 3 -- bounded reachability, unrolled by hand. FOUR steps.
;
; x starts at 0. Each step adds 1 or 2. Can x ever equal 7 within 4 steps?
; Yes, and four is the smallest k for which it is: 2+2+2+1.  Z3 hands back the
; trace that does it, which is the counterexample-as-witness idea again.
;
; This is a WORKED EXAMPLE on a different machine from the one the homework
; asks about. The technique is what transfers: unroll k steps, name a variable
; per step, constrain each transition, and ask whether the target appears.

(declare-const x0 Int) (declare-const x1 Int)
(declare-const x2 Int) (declare-const x3 Int)
(declare-const x4 Int)

(assert (= x0 0))
(assert (or (= x1 (+ x0 1)) (= x1 (+ x0 2))))
(assert (or (= x2 (+ x1 1)) (= x2 (+ x1 2))))
(assert (or (= x3 (+ x2 1)) (= x3 (+ x2 2))))
(assert (or (= x4 (+ x3 1)) (= x4 (+ x3 2))))

(assert (or (= x0 7) (= x1 7) (= x2 7) (= x3 7) (= x4 7)))

(check-sat)
(get-model)
