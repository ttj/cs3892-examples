/-
  Session 19 -- insertion sort, proved correct for EVERY list of integers.

  The specification has two halves, and a sort must meet both:
    • the output is in order (`Sorted`), and
    • the output is a rearrangement of the input (`List.Perm`): nothing lost, nothing added.
  Tests check a few lists; the theorem `isort_correct` covers all of them, of every length.

  Then a plausible bug (`isortBad` keeps one copy of a repeated value): its tests pass, it even
  returns sorted lists, and Lean checks a two-element counterexample to the second half.

  Finally Curry-Howard on this example: `isort_sorted` has the same recursion as `isort`, and
  `csort` is a program whose return type is the specification itself.
  python/07_sorting.py runs every region and asserts Lean's output; python/isort.py is the
  Python version the slides translate from.
-/
namespace S19

-- SLIDE: sort-def
/-- Put x in front of the first element that is ≥ x. -/
def insert (x : Int) : List Int → List Int
  | []      => [x]
  | y :: ys => if x ≤ y then x :: y :: ys else y :: insert x ys

/-- Insertion sort: sort the tail, then insert the head into it. -/
def isort : List Int → List Int
  | []      => []
  | x :: xs => insert x (isort xs)
-- END

-- SLIDE: sort-tests
#eval isort [5, 2, 9, 1, 5, 6]
#eval isort [3, -1, 0, -7]
#eval isort []
#guard isort [3, 1, 2] == [1, 2, 3]
#guard isort [2, 2, 1] == [1, 2, 2]
-- END

-- SLIDE: sort-spec
/-- `Sorted l`: every element is ≤ every element after it. -/
inductive Sorted : List Int → Prop
  | nil : Sorted []
  | cons (a : Int) (l : List Int) :
      (∀ b ∈ l, a ≤ b) → Sorted l → Sorted (a :: l)

/-- Correct: sorted, AND a permutation of the input. -/
def SortSpec (sort : List Int → List Int) : Prop :=
  ∀ l, Sorted (sort l) ∧ (sort l).Perm l
-- END

-- SLIDE: perm
/-- Inserting x is a rearrangement of putting x in front. -/
theorem insert_perm (x : Int) : ∀ l, (insert x l).Perm (x :: l)
  | []      => List.Perm.refl _
  | y :: ys => by
    unfold insert
    split
    · exact List.Perm.refl _            -- x ≤ y: nothing moves
    · -- y :: insert x ys  ~  y :: x :: ys  ~  x :: y :: ys
      exact ((insert_perm x ys).cons y).trans (List.Perm.swap x y ys)

/-- So insertion sort is a rearrangement of its input. -/
theorem isort_perm : ∀ l, (isort l).Perm l
  | []      => List.Perm.refl _
  | x :: xs => (insert_perm x (isort xs)).trans ((isort_perm xs).cons x)
-- END

-- SLIDE: sorted
/-- Inserting into a sorted list keeps it sorted. -/
theorem insert_sorted (x : Int) : ∀ l, Sorted l → Sorted (insert x l)
  | [], _ => Sorted.cons x [] (by simp) Sorted.nil
  | y :: ys, Sorted.cons _ _ hy hys => by
    unfold insert
    split
    · next hxy =>                                     -- x ≤ y: x goes in front
      refine Sorted.cons x (y :: ys) ?_ (Sorted.cons y ys hy hys)
      intro b hb
      simp only [List.mem_cons] at hb
      rcases hb with rfl | hb
      · exact hxy
      · have := hy b hb; omega
    · next hxy =>                                     -- y < x: y stays in front
      refine Sorted.cons y (insert x ys) ?_ (insert_sorted x ys hys)
      intro b hb
      have hb := (insert_perm x ys).mem_iff.mp hb     -- by half one
      simp only [List.mem_cons] at hb
      rcases hb with rfl | hb
      · omega
      · exact hy b hb

/-- So insertion sort's output is sorted. -/
theorem isort_sorted : ∀ l, Sorted (isort l)
  | []      => Sorted.nil
  | x :: xs => insert_sorted x (isort xs) (isort_sorted xs)
-- END

-- SLIDE: correct
/-- The theorem: isort is a correct sort, for every list. -/
theorem isort_correct : SortSpec isort :=
  fun l => ⟨isort_sorted l, isort_perm l⟩

#print axioms isort_correct
-- END

-- SLIDE: bad
/-- A plausible bug: on a tie, keep one copy. -/
def insertBad (x : Int) : List Int → List Int
  | []      => [x]
  | y :: ys => if x < y then x :: y :: ys
               else if x = y then y :: ys
               else y :: insertBad x ys

def isortBad : List Int → List Int
  | []      => []
  | x :: xs => insertBad x (isortBad xs)

#guard isortBad [3, 1, 2] == [1, 2, 3]   -- the tests pass
#guard isortBad [5, 2, 9, 1] == [1, 2, 5, 9]

/-- Lean checks the counterexample: two equal elements in, one out. -/
theorem isortBad_wrong : ¬ SortSpec isortBad := by
  intro h
  have := (h [1, 1]).2       -- would need [1] ~ [1, 1]
  simp [isortBad, insertBad] at this
-- END

-- SLIDE: ch-sort
/-- The return type IS the spec: the value carries its proof. -/
def csort (l : List Int) : { r : List Int // Sorted r ∧ r.Perm l } :=
  ⟨isort l, isort_sorted l, isort_perm l⟩

#eval (csort [3, 1, 2]).val
-- END

end S19
