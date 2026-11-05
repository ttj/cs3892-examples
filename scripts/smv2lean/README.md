# smv2lean: SMV → Lean 4

This is the course's copy of the translator from [ttj/leansmv](https://github.com/ttj/leansmv)
(`scripts/`, commit `2349edc`, 2026-05-23), unchanged. It parses a NuSMV/nuXmv model and emits
a Lean 4 transition system:

| SMV | Lean |
|---|---|
| `VAR x : {off, on}` | `inductive ModeVal` with one constructor per value |
| `VAR x : boolean`, `x : 0..25` | a `Bool` / `Nat` field of a `State` structure (**the range is dropped**) |
| `init(x) := …` | the `init` predicate |
| `next(x) := case … esac` | an `if … then … else if …` chain in the step relation, one branch per case line |
| a variable with no `init`/`next` (a free input) | `∃ x' : …` in the step relation |
| `DEFINE` | inlined |
| `INVARSPEC p` | a commented `theorem … : Invariant <Name>TS (fun s => p)` stub to prove |

`to_course.py` runs it and retargets the output from leansmv's `VerifDemo.TransitionSystem`
to a session's own `TS` (the definitions HW4's `Defs.lean` gives you): `TransitionSystem` →
`TS`, `next` → `step`, and the file goes inside the session's namespace.

```bash
pip install lark                      # the parser library (once)
python3 scripts/smv2lean/to_course.py sessions/<session>/smv/counter.smv S20   # prints the Lean
```

Session 20 uses it on the two-mode counter and on session 11's mutex; its
`python/08_smv_to_lean.py` regenerates both and checks they match the committed files.
