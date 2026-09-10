; EXPECT: sat
; Slide 31 -- "Demo 4: arithmetic your machine does not do"
;
; Is x + 1 > x ever false? In mathematics, no. On a machine, yes -- and the
; solver hands back the exact value where it breaks: 127, because signed 8-bit
; 127 + 1 = -128. This is the class of bug that destroyed Ariane 5 flight 501.

(declare-const x (_ BitVec 8))
(assert (not (bvsgt (bvadd x #x01) x)))
(check-sat)
(get-model)
