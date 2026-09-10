; EXPECT: unsat
; HW1 part 3 -- bounded reachability, unrolled by hand. THREE steps.
;
; x starts at 0. Each step adds 1 or 2. Can x ever equal 7 within 3 steps?
; No: the most three steps can add is 6.
;
; This is a WORKED EXAMPLE on a different machine from the one the homework
; asks about. The technique is what transfers: unroll k steps, name a variable
; per step, constrain each transition, and ask whether the target appears.

(declare-const x0 Int) (declare-const x1 Int)
(declare-const x2 Int) (declare-const x3 Int)

(assert (= x0 0))
(assert (or (= x1 (+ x0 1)) (= x1 (+ x0 2))))
(assert (or (= x2 (+ x1 1)) (= x2 (+ x1 2))))
(assert (or (= x3 (+ x2 1)) (= x3 (+ x2 2))))

(assert (or (= x0 7) (= x1 7) (= x2 7) (= x3 7)))

(check-sat)
