; EXPECT: unsat
; Slide 29 -- "Demo 2: one atom becomes arithmetic"
;
; Same policy, one atom richer. `e` was an opaque boolean; `months >= 12` is a
; constraint the solver can reason about. Nobody tells Z3 that 11 < 12 -- the
; Int sort carries a theory of arithmetic with it, and that is the whole point.

(declare-const months Int)
(declare-const u Bool)
(declare-const c Bool)
(declare-const L Bool)

(assert (= L (and (>= months 12) u (not c))))
(assert (= months 11))
(assert L)

(check-sat)
