#!/usr/bin/env python3
"""
smv2lean: Translate NuXMV (.smv) models into Lean 4 transition system definitions.

Usage: python smv2lean.py <input.smv> [output.lean]

Reuses the Lark-based parser from the smvis project. Generates Lean 4 code
that instantiates the TransitionSystem framework from VerifDemo.TransitionSystem.
"""
from __future__ import annotations
import sys
import os
import textwrap

# Ensure the scripts directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smv_model import (
    SmvModel, VarDecl, BoolType, EnumType, RangeType,
    IntLit, BoolLit, VarRef, NextRef, BinOp, UnaryOp, CaseExpr, SetExpr, SpecDecl,
)
from smv_parser import parse_smv_file


def _lean_name(name: str) -> str:
    """Convert an SMV identifier to a valid Lean identifier."""
    return name.replace(".", "_")


def _capitalize(name: str) -> str:
    """Capitalize first letter for Lean type names."""
    return name[0].upper() + name[1:] if name else name


def _eval_const(expr, defines: dict) -> int | None:
    """Try to evaluate an expression to a constant integer."""
    if isinstance(expr, IntLit):
        return expr.value
    if isinstance(expr, VarRef) and expr.name in defines:
        return _eval_const(defines[expr.name], defines)
    if isinstance(expr, BinOp):
        l = _eval_const(expr.left, defines)
        r = _eval_const(expr.right, defines)
        if l is not None and r is not None:
            ops = {"+": l + r, "-": l - r, "*": l * r, "/": l // r, "mod": l % r}
            if expr.op in ops:
                return ops[expr.op]
    if isinstance(expr, UnaryOp) and expr.op == "-":
        v = _eval_const(expr.operand, defines)
        if v is not None:
            return -v
    return None


def _inline_defines(expr, defines: dict):
    """Recursively inline DEFINE references in an expression."""
    if isinstance(expr, VarRef) and expr.name in defines:
        return _inline_defines(defines[expr.name], defines)
    if isinstance(expr, BinOp):
        return BinOp(expr.op,
                     _inline_defines(expr.left, defines),
                     _inline_defines(expr.right, defines))
    if isinstance(expr, UnaryOp):
        return UnaryOp(expr.op, _inline_defines(expr.operand, defines))
    if isinstance(expr, CaseExpr):
        return CaseExpr([
            (_inline_defines(c, defines), _inline_defines(v, defines))
            for c, v in expr.branches
        ])
    return expr


class SmvToLean:
    """Generates Lean 4 code from an SmvModel."""

    def __init__(self, model: SmvModel, model_name: str = "Model",
                 source_file: str = ""):
        self.model = model
        self.model_name = model_name
        self.source_file = source_file
        self.lines: list[str] = []
        # Identify enum types that need their own inductive
        self.enum_types: dict[str, list[str]] = {}  # lean_type_name -> values
        # Identify nondeterministic inputs (vars with no init/next)
        self.input_vars: list[str] = []
        self.state_vars: list[str] = []
        self._classify_vars()

    def _classify_vars(self):
        for name, vd in self.model.variables.items():
            has_init = name in self.model.inits
            has_next = name in self.model.nexts
            if not has_init and not has_next:
                self.input_vars.append(name)
            else:
                self.state_vars.append(name)
            if isinstance(vd.var_type, EnumType):
                type_name = _capitalize(_lean_name(name)) + "Val"
                self.enum_types[type_name] = vd.var_type.values

    def _lean_type_for_var(self, name: str) -> str:
        vd = self.model.variables[name]
        vt = vd.var_type
        if isinstance(vt, BoolType):
            return "Bool"
        if isinstance(vt, EnumType):
            return _capitalize(_lean_name(name)) + "Val"
        if isinstance(vt, RangeType):
            return "Nat"
        raise ValueError(f"Unknown type for {name}: {vt}")

    def _is_bool_var(self, expr) -> bool:
        """True if expr is a VarRef to a boolean-typed variable."""
        if isinstance(expr, VarRef):
            vd = self.model.variables.get(expr.name)
            if vd and isinstance(vd.var_type, BoolType):
                return True
        return False

    def _expr_to_lean(self, expr, prefix: str = "s", prop_ctx: bool = False) -> str:
        """Convert an SMV expression to a Lean expression string.
        prefix is the state variable name (e.g., 's' for current, 's'' for next).
        prop_ctx indicates we're in a Prop context (inside ∧/∨/¬/→/if-cond),
        so Bool-typed variable references are emitted as `s.v = true`."""
        if isinstance(expr, IntLit):
            return str(expr.value)
        if isinstance(expr, BoolLit):
            return "true" if expr.value else "false"
        if isinstance(expr, VarRef):
            # Check if it's a DEFINE
            if expr.name in self.model.defines:
                inlined = _inline_defines(expr, self.model.defines)
                return self._expr_to_lean(inlined, prefix, prop_ctx)
            ln = _lean_name(expr.name)
            vd = self.model.variables.get(expr.name)
            # If a Bool variable appears in Prop context, make it `s.v = true`
            if vd and isinstance(vd.var_type, BoolType) and prop_ctx:
                return f"({prefix}.{ln} = true)"
            return f"{prefix}.{ln}"
        if isinstance(expr, NextRef):
            # next(x) in a condition refers to the next state s'.x
            ln = _lean_name(expr.name)
            vd = self.model.variables.get(expr.name)
            if vd and isinstance(vd.var_type, BoolType) and prop_ctx:
                return f"(s'.{ln} = true)"
            return f"s'.{ln}"
        if isinstance(expr, BinOp):
            op = expr.op
            # Check if either side is an enum literal comparison
            if op == "=":
                l = self._expr_to_lean(expr.left, prefix, False)
                r = self._expr_to_lean(expr.right, prefix, False)
                l_enum = self._try_enum_literal(expr.left)
                r_enum = self._try_enum_literal(expr.right)
                if l_enum:
                    l = l_enum
                if r_enum:
                    r = r_enum
                return f"({l} = {r})"
            if op == "!=":
                l = self._expr_to_lean(expr.left, prefix, False)
                r = self._expr_to_lean(expr.right, prefix, False)
                l_enum = self._try_enum_literal(expr.left)
                r_enum = self._try_enum_literal(expr.right)
                if l_enum:
                    l = l_enum
                if r_enum:
                    r = r_enum
                return f"({l} ≠ {r})"
            if op == "&":
                l = self._expr_to_lean(expr.left, prefix, True)
                r = self._expr_to_lean(expr.right, prefix, True)
                return f"({l} ∧ {r})"
            if op == "|":
                l = self._expr_to_lean(expr.left, prefix, True)
                r = self._expr_to_lean(expr.right, prefix, True)
                return f"({l} ∨ {r})"
            if op == "->":
                l = self._expr_to_lean(expr.left, prefix, True)
                r = self._expr_to_lean(expr.right, prefix, True)
                return f"({l} → {r})"
            if op == ">=":
                l = self._expr_to_lean(expr.left, prefix, False)
                r = self._expr_to_lean(expr.right, prefix, False)
                return f"({l} ≥ {r})"
            if op == "<=":
                l = self._expr_to_lean(expr.left, prefix, False)
                r = self._expr_to_lean(expr.right, prefix, False)
                return f"({l} ≤ {r})"
            if op in ("<", ">", "+", "-", "*"):
                l = self._expr_to_lean(expr.left, prefix, False)
                r = self._expr_to_lean(expr.right, prefix, False)
                return f"({l} {op} {r})"
            l = self._expr_to_lean(expr.left, prefix, prop_ctx)
            r = self._expr_to_lean(expr.right, prefix, prop_ctx)
            return f"({l} {op} {r})"
        if isinstance(expr, UnaryOp):
            if expr.op == "!":
                # !b where b is Bool → b = false; otherwise ¬b
                if self._is_bool_var(expr.operand):
                    ln = _lean_name(expr.operand.name)
                    return f"({prefix}.{ln} = false)"
                operand = self._expr_to_lean(expr.operand, prefix, True)
                return f"(¬{operand})"
            if expr.op == "-":
                operand = self._expr_to_lean(expr.operand, prefix, False)
                return f"(-{operand})"
            operand = self._expr_to_lean(expr.operand, prefix, prop_ctx)
            return f"({expr.op} {operand})"
        if isinstance(expr, CaseExpr):
            return self._case_to_lean(expr, prefix)
        raise ValueError(f"Cannot convert expression: {expr}")

    def _try_enum_literal(self, expr) -> str | None:
        """If expr is a VarRef that matches an enum value, return its Lean dotted name."""
        if isinstance(expr, VarRef):
            for type_name, values in self.enum_types.items():
                if expr.name in values:
                    return f".{_lean_name(expr.name)}"
        return None

    def _case_to_lean(self, case: CaseExpr, prefix: str) -> str:
        """Convert a case expression to nested if-then-else."""
        parts = []
        for i, (cond, val) in enumerate(case.branches):
            cond_str = self._expr_to_lean(cond, prefix, prop_ctx=True)
            val_str = self._expr_to_lean(val, prefix)
            # Check for enum literals in value
            val_enum = self._try_enum_literal(val)
            if val_enum:
                val_str = val_enum
            if isinstance(cond, BoolLit) and cond.value:
                # TRUE branch -- this is the default
                parts.append(val_str)
            elif i == 0:
                parts.append(f"if {cond_str} then {val_str}")
            else:
                parts.append(f"else if {cond_str} then {val_str}")
        if not any(isinstance(c, BoolLit) and c.value for c, _ in case.branches):
            # No TRUE default -- add a fallback (should not happen in well-formed SMV)
            parts.append(f"else {parts[-1].split('then ')[-1]}")
        else:
            # The last part is the default value, prepend "else"
            last = parts.pop()
            parts.append(f"else {last}")
        return "\n      ".join(parts)

    def _spec_expr_to_lean(self, expr, prefix: str = "s") -> str:
        """Convert an INVARSPEC expression to Lean (always Prop context)."""
        return self._expr_to_lean(expr, prefix, prop_ctx=True)

    def generate(self) -> str:
        """Generate the full Lean 4 file."""
        self.lines = []

        # ---- File-header comment block -----------------------------------
        # An explanatory preamble so a CS student opening the file can
        # immediately see what it is and where the real proofs live.
        src_basename = (
            os.path.basename(self.source_file) if self.source_file else "<unknown>.smv"
        )
        proofs_module = f"VerifDemo.NuXMV.{self.model_name}Proofs"
        self._emit("/-")
        self._emit(f"  {self.model_name} — auto-generated from `{src_basename}`")
        self._emit("  " + "=" * (len(self.model_name) + 36))
        self._emit("")
        self._emit(f"  This file was produced by `scripts/smv2lean.py` from the SMV")
        self._emit(f"  source `{src_basename}`. It contains:")
        self._emit("")
        self._emit("    • Lean encodings of the SMV variable types (enums become")
        self._emit("      `inductive`s, booleans become `Bool`, ranges become `Nat`).")
        self._emit("    • A `State` structure holding all variables of the model.")
        self._emit("    • A `TransitionSystem` value (`<name>TS`) capturing the SMV")
        self._emit("      `init` and `next` clauses. Nondeterministic SMV inputs")
        self._emit("      become existentially-quantified variables in `next`.")
        self._emit("    • For each `INVARSPEC` in the SMV, a COMMENTED Lean `theorem`")
        self._emit("      stub (so this file stays sorry-free). Uncomment one and prove")
        self._emit(f"      it; completed proofs live in `{proofs_module}`.")
        self._emit("")
        self._emit("  Do NOT hand-edit this file: it will be overwritten by the next")
        self._emit("  run of `smv2lean.py`. Add proofs in the corresponding")
        self._emit("  `*Proofs.lean` file instead.")
        self._emit("-/")
        self._emit("import VerifDemo.TransitionSystem")
        self._emit("")

        # Enum type declarations
        for type_name, values in self.enum_types.items():
            vals = " | ".join(_lean_name(v) for v in values)
            self._emit(f"inductive {type_name} where")
            for v in values:
                self._emit(f"  | {_lean_name(v)}")
            self._emit(f"  deriving DecidableEq, Repr")
            self._emit("")
            self._emit(f"open {type_name}")
            self._emit("")

        # State structure
        state_name = f"{self.model_name}State"
        self._emit(f"structure {state_name} where")
        for name in self.model.variables:
            ln = _lean_name(name)
            lt = self._lean_type_for_var(name)
            self._emit(f"  {ln} : {lt}")
        self._emit(f"  deriving DecidableEq, Repr")
        self._emit("")

        # Transition system definition
        ts_name = _lean_name(self.model_name) + "TS"
        self._emit(f"def {ts_name} : TransitionSystem {state_name} where")

        # Init predicate
        init_parts = []
        for name in self.state_vars:
            if name in self.model.inits:
                init_expr = _inline_defines(self.model.inits[name], self.model.defines)
                ln = _lean_name(name)
                val = self._expr_to_lean(init_expr, "s")
                val_enum = self._try_enum_literal(init_expr)
                if val_enum:
                    val = val_enum
                init_parts.append(f"s.{ln} = {val}")
        if init_parts:
            self._emit(f"  init s := {' ∧ '.join(init_parts)}")
        else:
            self._emit(f"  init _ := True")

        # Next relation
        self._emit(f"  next s s' :=")
        # Existentially quantify nondeterministic inputs
        if self.input_vars:
            for iv in self.input_vars:
                ln = _lean_name(iv)
                lt = self._lean_type_for_var(iv)
                self._emit(f"    ∃ {ln}' : {lt},")
            # Bind input variables in s'
            input_bindings = []
            for iv in self.input_vars:
                ln = _lean_name(iv)
                input_bindings.append(f"s'.{ln} = {ln}'")
            self._emit(f"    {' ∧ '.join(input_bindings)} ∧")

        # Next-state assignments for each state variable
        next_parts = []
        for name in self.state_vars:
            if name in self.model.nexts:
                next_expr = _inline_defines(self.model.nexts[name], self.model.defines)
                ln = _lean_name(name)
                lean_expr = self._next_assign_to_lean(name, next_expr)
                next_parts.append(lean_expr)
            elif name in self.model.inits and name not in self.model.nexts:
                # Has init but no next -- stays the same
                ln = _lean_name(name)
                next_parts.append(f"s'.{ln} = s.{ln}")

        indent = "    "
        for i, part in enumerate(next_parts):
            if i < len(next_parts) - 1:
                for j, line in enumerate(part.split("\n")):
                    self._emit(f"{indent}{line}")
                self._emit(f"{indent}∧")
            else:
                for j, line in enumerate(part.split("\n")):
                    self._emit(f"{indent}{line}")

        self._emit("")

        # INVARSPEC theorems — emitted as COMMENTED stubs, NOT `sorry`-typed
        # theorems. This keeps the generated file sorry-free (so a project that
        # imports it stays sorry-free) and never asserts a deliberately-false
        # sampler spec via `sorry`. To do the exercise, uncomment one and prove
        # it; if it is a deliberately-false spec, prove its negation instead
        # (`example : ¬ Invariant … := …`). Completed proofs live in the
        # matching `<Name>Proofs.lean`.
        spec_count = 0
        for spec in self.model.specs:
            if spec.kind == "INVARSPEC":
                spec_count += 1
                prop_str = self._spec_expr_to_lean(spec.expr, "s")
                self._emit(f"-- INVARSPEC {spec_count} (from {src_basename}): "
                           f"{self._spec_to_comment(spec.expr)}")
                self._emit(f"--   Exercise: uncomment and prove (or, if false, prove its negation);")
                self._emit(f"--   completed proofs go in {proofs_module}.")
                self._emit(f"-- theorem {ts_name}_inv{spec_count} :")
                self._emit(f"--     Invariant {ts_name} (fun s => {prop_str}) := by")
                self._emit(f"--   sorry")
                self._emit("")

        return "\n".join(self.lines)

    def _next_assign_to_lean(self, var_name: str, expr) -> str:
        """Generate a next-state assignment for a variable."""
        ln = _lean_name(var_name)
        if isinstance(expr, CaseExpr):
            return self._next_case_to_lean(var_name, expr)
        # Simple expression (possibly a set for nondeterministic choice)
        return self._next_value_to_lean(var_name, expr)

    def _next_value_to_lean(self, var_name: str, val) -> str:
        """Generate the Lean assertion s'.var = val (or disjunction for set values)."""
        ln = _lean_name(var_name)
        if isinstance(val, SetExpr):
            parts = []
            for v in val.values:
                v_str = self._expr_to_lean(v, "s")
                v_enum = self._try_enum_literal(v)
                if v_enum:
                    v_str = v_enum
                parts.append(f"s'.{ln} = {v_str}")
            return "(" + " ∨ ".join(parts) + ")"
        val_str = self._expr_to_lean(val, "s")
        val_enum = self._try_enum_literal(val)
        if val_enum:
            val_str = val_enum
        return f"s'.{ln} = {val_str}"

    def _next_case_to_lean(self, var_name: str, case: CaseExpr) -> str:
        """Convert a next(var) case expression into a Lean equality chain."""
        ln = _lean_name(var_name)
        lines = []
        has_true_default = False
        for i, (cond, val) in enumerate(case.branches):
            cond_str = self._expr_to_lean(cond, "s", prop_ctx=True)
            val_assertion = self._next_value_to_lean(var_name, val)
            if isinstance(cond, BoolLit) and cond.value:
                # TRUE default
                has_true_default = True
                if i == 0:
                    lines.append(f"{val_assertion}")
                else:
                    lines.append(f"else {val_assertion}")
            elif i == 0:
                lines.append(f"(if {cond_str} then {val_assertion}")
            else:
                lines.append(f"else if {cond_str} then {val_assertion}")

        # If no TRUE default, append a self-stay fallback so the `if` chain is complete
        if not has_true_default and len(lines) >= 1:
            lines.append(f"else s'.{ln} = s.{ln}")

        # Close with a paren
        if len(lines) > 1:
            last = lines[-1]
            lines[-1] = last + ")"
        return "\n".join(lines)

    def _spec_to_comment(self, expr) -> str:
        """Convert a spec expression to a readable comment."""
        from smv_model import expr_to_str
        return expr_to_str(expr)

    def _emit(self, line: str):
        self.lines.append(line)


def main():
    if len(sys.argv) < 2:
        print("Usage: python smv2lean.py <input.smv> [output.lean]", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        output_path = None

    # Derive model name from filename
    basename = os.path.splitext(os.path.basename(input_path))[0]
    model_name = _capitalize(basename)

    model = parse_smv_file(input_path)
    gen = SmvToLean(model, model_name, source_file=input_path)
    lean_code = gen.generate()

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(lean_code + "\n")
        print(f"Generated {output_path}")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(lean_code)


if __name__ == "__main__":
    main()
