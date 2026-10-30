/-
  Session 21 -- what Cslib v4.33.0 proves about the automata of sessions 12 and 14, read with
  #check (the statement) and #print axioms (what it rests on). Nothing here is proved by us: these
  are Cslib's theorems, checked by Lean's kernel when Cslib was built.
-/
import Cslib.Logics.HML.Basic
import Cslib.Foundations.Semantics.LTS.Bisimulation
import Cslib.Computability.Automata.NA.BuchiInter
import Cslib.Computability.Languages.OmegaRegularLanguage

open Cslib

-- SLIDE: hm
-- Hennessy-Milner: same HML theory iff bisimilar (for image-finite LTSs)
#check @Logic.HML.theoryEq_eq_bisimilarity
-- trace equivalence is not bisimilarity (session 14's vending machines)
#check @LTS.Bisimilarity.bisimilarity_neq_traceEq
-- END

-- SLIDE: buchi
-- the intersection of two Buchi automata accepts the intersection of their languages
#check @Automata.NA.Buchi.inter_language_eq
-- some omega-regular language has no deterministic Buchi automaton
#check @ωLanguage.IsRegular.not_da_buchi
-- the complement of an omega-regular language is omega-regular
#check @ωLanguage.IsRegular.compl
-- END

-- SLIDE: axioms
#print axioms Logic.HML.theoryEq_eq_bisimilarity
#print axioms Automata.NA.Buchi.inter_language_eq
#print axioms ωLanguage.IsRegular.not_da_buchi
#print axioms ωLanguage.IsRegular.compl
-- END
