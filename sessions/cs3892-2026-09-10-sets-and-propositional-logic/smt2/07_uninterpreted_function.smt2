; EXPECT: unsat
; Slide 32 -- "Demo 5: reasoning about code you cannot see"
;
; Z3 has never seen `f`. No body, no definition. It knows exactly one thing:
; f is a function, so equal inputs give equal outputs (congruence). That alone
; refutes this -- and it is how a verifier reasons about a library call it has
; no source for.

(declare-fun f (Int) Int)
(declare-const a Int)
(declare-const b Int)

(assert (= a b))
(assert (not (= (f a) (f b))))

(check-sat)
