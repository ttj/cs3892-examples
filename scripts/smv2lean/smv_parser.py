"""SMV file parser using Lark. Parses the nuXmv subset used in EECS 6315 models."""
from __future__ import annotations
import os
from lark import Lark, Transformer, Token
from smv_model import (
    SmvModel, VarDecl, BoolType, EnumType, RangeType,
    IntLit, BoolLit, VarRef, NextRef, BinOp, UnaryOp,
    CaseExpr, SetExpr, TemporalUnary, TemporalBinary, SpecDecl,
)

_GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), "smv_grammar.lark")

_parser = None

def _get_parser():
    global _parser
    if _parser is None:
        with open(_GRAMMAR_PATH, "r") as f:
            grammar_text = f.read()
        _parser = Lark(grammar_text, parser="lalr")
    return _parser


# Sentinel used to mark process instance declarations in the VAR section.
_PROCESS_MARKER = "__PROCESS__"


class SmvTransformer(Transformer):
    """Transforms the Lark parse tree into SmvModel dataclasses."""

    # ---- Terminals ----
    def IDENT(self, token):
        return str(token)

    def INT(self, token):
        return int(token)

    # ---- Module headers ----
    def param_header(self, args):
        return (str(args[0]), args[1])  # (name, param_list)

    def simple_header(self, args):
        return (str(args[0]), [])       # (name, no params)

    # ---- Variable types ----
    def bool_type(self, args):
        return BoolType()

    def enum_type(self, args):
        return EnumType(args[0])

    def ident_list(self, args):
        return list(args)

    def range_type(self, args):
        # Bounds may be int (literal) or str (DEFINE reference, resolved later)
        lo = args[0] if isinstance(args[0], str) else int(args[0])
        hi = args[1] if isinstance(args[1], str) else int(args[1])
        return RangeType(lo, hi)

    def neg_bound(self, args):
        return -args[0]

    def pos_bound(self, args):
        return args[0]

    def ident_bound(self, args):
        return str(args[0])

    def process_type(self, args):
        """Process instantiation: process ModuleName(arg1, arg2, ...)"""
        module_name = str(args[0])
        arg_names = args[1] if len(args) > 1 else []
        return (_PROCESS_MARKER, module_name, arg_names)

    def process_type_noargs(self, args):
        """Process instantiation with no arguments: process ModuleName()"""
        module_name = str(args[0])
        return (_PROCESS_MARKER, module_name, [])

    # ---- Expressions: literals and references ----
    def var_ref(self, args):
        return VarRef(str(args[0]))

    def int_lit(self, args):
        return IntLit(int(args[0]))

    def true_const(self, args):
        return BoolLit(True)

    def false_const(self, args):
        return BoolLit(False)

    def next_ref(self, args):
        return NextRef(str(args[0]))

    def unary_minus(self, args):
        # Optimize: if operand is IntLit, fold to negative IntLit
        if isinstance(args[0], IntLit):
            return IntLit(-args[0].value)
        return UnaryOp("-", args[0])

    # ---- Boolean / comparison operators ----
    def neg_op(self, args):
        return UnaryOp("!", args[0])

    def impl_op(self, args):
        return BinOp("->", args[0], args[1])

    def or_op(self, args):
        return BinOp("|", args[0], args[1])

    def and_op(self, args):
        return BinOp("&", args[0], args[1])

    def eq_op(self, args):
        return BinOp("=", args[0], args[1])

    def ne_op(self, args):
        return BinOp("!=", args[0], args[1])

    def ge_op(self, args):
        return BinOp(">=", args[0], args[1])

    def le_op(self, args):
        return BinOp("<=", args[0], args[1])

    def gt_op(self, args):
        return BinOp(">", args[0], args[1])

    def lt_op(self, args):
        return BinOp("<", args[0], args[1])

    # ---- Arithmetic operators ----
    def add_op(self, args):
        return BinOp("+", args[0], args[1])

    def sub_op(self, args):
        return BinOp("-", args[0], args[1])

    def mul_op(self, args):
        return BinOp("*", args[0], args[1])

    def div_op(self, args):
        return BinOp("/", args[0], args[1])

    def mod_op(self, args):
        return BinOp("mod", args[0], args[1])

    # ---- Temporal operators ----
    def ag_op(self, args):
        return TemporalUnary("AG", args[0])

    def af_op(self, args):
        return TemporalUnary("AF", args[0])

    def ax_op(self, args):
        return TemporalUnary("AX", args[0])

    def eg_op(self, args):
        return TemporalUnary("EG", args[0])

    def ef_op(self, args):
        return TemporalUnary("EF", args[0])

    def ex_op(self, args):
        return TemporalUnary("EX", args[0])

    def g_op(self, args):
        return TemporalUnary("G", args[0])

    def f_op(self, args):
        return TemporalUnary("F", args[0])

    def x_op(self, args):
        return TemporalUnary("X", args[0])

    def until_op(self, args):
        return TemporalBinary("U", args[0], args[1])

    # ---- Case / Set expressions ----
    def case_expr(self, args):
        return CaseExpr(list(args))

    def case_branch(self, args):
        return (args[0], args[1])

    def set_expr(self, args):
        return SetExpr(list(args))

    # ---- Variable declarations ----
    def var_decl(self, args):
        name = str(args[0])
        type_or_proc = args[1]
        if isinstance(type_or_proc, tuple) and type_or_proc[0] == _PROCESS_MARKER:
            # Process instance: return marker tuple
            _, mod_name, mod_args = type_or_proc
            return (_PROCESS_MARKER, name, mod_name, mod_args)
        return VarDecl(name, type_or_proc)

    def var_section(self, args):
        return ("VAR", list(args))

    # ---- DEFINE ----
    def define_decl(self, args):
        return (str(args[0]), args[1])

    def define_section(self, args):
        return ("DEFINE", list(args))

    # ---- ASSIGN ----
    def init_assign(self, args):
        return ("init", str(args[0]), args[1])

    def next_assign(self, args):
        return ("next", str(args[0]), args[1])

    def assign_section(self, args):
        return ("ASSIGN", list(args))

    # ---- FAIRNESS ----
    def fairness_decl(self, args):
        return ("FAIRNESS", args[0])

    # ---- Specifications ----
    def invarspec(self, args):
        return ("SPEC", SpecDecl("INVARSPEC", args[0]))

    def ctlspec(self, args):
        return ("SPEC", SpecDecl("CTLSPEC", args[0]))

    def ltlspec(self, args):
        return ("SPEC", SpecDecl("LTLSPEC", args[0]))

    def spec_default(self, args):
        return ("SPEC", SpecDecl("SPEC", args[0]))

    # ---- Module ----
    def module(self, args):
        """Process a MODULE declaration and its sections into a dict."""
        header = args[0]   # (name, params) from module_header
        sections = args[1:]

        mod_data = {
            "name": header[0],
            "params": header[1],
            "variables": {},
            "defines": {},
            "inits": {},
            "nexts": {},
            "fairness": [],
            "specs": [],
            "process_instances": [],
        }

        for item in sections:
            if item is None:
                continue
            kind = item[0]
            if kind == "VAR":
                for vd in item[1]:
                    if isinstance(vd, tuple) and vd[0] == _PROCESS_MARKER:
                        mod_data["process_instances"].append(vd)
                    else:
                        mod_data["variables"][vd.name] = vd
            elif kind == "DEFINE":
                for name, expr in item[1]:
                    mod_data["defines"][name] = expr
            elif kind == "ASSIGN":
                for a in item[1]:
                    if a[0] == "init":
                        mod_data["inits"][a[1]] = a[2]
                    elif a[0] == "next":
                        mod_data["nexts"][a[1]] = a[2]
            elif kind == "FAIRNESS":
                mod_data["fairness"].append(item[1])
            elif kind == "SPEC":
                mod_data["specs"].append(item[1])

        return mod_data

    # ---- Top-level ----
    def start(self, args):
        modules = [m for m in args if m is not None]

        # Check if any module has process instances
        has_processes = any(m["process_instances"] for m in modules)

        if not has_processes and len(modules) == 1:
            # Single module, no processes: build SmvModel directly (fast path)
            mod = modules[0]
            model = SmvModel()
            model.variables = mod["variables"]
            model.defines = mod["defines"]
            model.inits = mod["inits"]
            model.nexts = mod["nexts"]
            model.fairness = mod["fairness"]
            model.specs = mod["specs"]
            return model

        # Multi-module or has process instances: flatten
        from smv_flattener import flatten_modules
        return flatten_modules(modules)


_transformer = SmvTransformer()


def _eval_const_expr(expr, defines: dict) -> int:
    """Evaluate a constant expression (DEFINE body) to an integer."""
    if isinstance(expr, IntLit):
        return expr.value
    if isinstance(expr, VarRef):
        # Recursive DEFINE lookup
        if expr.name in defines:
            return _eval_const_expr(defines[expr.name], defines)
        raise ValueError(f"Cannot resolve '{expr.name}' to an integer")
    if isinstance(expr, BinOp):
        l = _eval_const_expr(expr.left, defines)
        r = _eval_const_expr(expr.right, defines)
        ops = {"+": l + r, "-": l - r, "*": l * r, "/": l // r, "mod": l % r}
        if expr.op in ops:
            return ops[expr.op]
    if isinstance(expr, UnaryOp) and expr.op == "-":
        return -_eval_const_expr(expr.operand, defines)
    raise ValueError(f"Cannot evaluate expression to integer: {expr}")


def _resolve_range_bounds(model: SmvModel):
    """Resolve DEFINE references in range bounds to integer values."""
    for vd in model.variables.values():
        if isinstance(vd.var_type, RangeType):
            rt = vd.var_type
            if isinstance(rt.lo, str):
                if rt.lo in model.defines:
                    rt.lo = _eval_const_expr(model.defines[rt.lo], model.defines)
                else:
                    raise ValueError(
                        f"Range bound '{rt.lo}' for variable '{vd.name}' "
                        f"is not defined"
                    )
            if isinstance(rt.hi, str):
                if rt.hi in model.defines:
                    rt.hi = _eval_const_expr(model.defines[rt.hi], model.defines)
                else:
                    raise ValueError(
                        f"Range bound '{rt.hi}' for variable '{vd.name}' "
                        f"is not defined"
                    )


def parse_smv(text: str) -> SmvModel:
    """Parse an SMV model string and return an SmvModel."""
    parser = _get_parser()
    tree = parser.parse(text)
    model = _transformer.transform(tree)
    _resolve_range_bounds(model)
    return model


def parse_smv_file(filepath: str) -> SmvModel:
    """Parse an SMV file and return an SmvModel."""
    with open(filepath, "r") as f:
        text = f.read()
    return parse_smv(text)
