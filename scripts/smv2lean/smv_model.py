"""Dataclasses for the SMV model intermediate representation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union


# --- Variable Types ---

@dataclass
class BoolType:
    pass

@dataclass
class EnumType:
    values: list[str]

@dataclass
class RangeType:
    lo: int | str  # str = DEFINE reference, resolved after parsing
    hi: int | str

VarType = Union[BoolType, EnumType, RangeType]


@dataclass
class VarDecl:
    name: str
    var_type: VarType


# --- Expression AST ---

@dataclass
class IntLit:
    value: int

@dataclass
class BoolLit:
    value: bool

@dataclass
class VarRef:
    name: str

@dataclass
class NextRef:
    """Reference to next(var) inside a condition."""
    name: str

@dataclass
class BinOp:
    op: str
    left: Expr
    right: Expr

@dataclass
class UnaryOp:
    op: str
    operand: Expr

@dataclass
class CaseExpr:
    branches: list[tuple[Expr, Expr]]  # (condition, value)

@dataclass
class SetExpr:
    """Non-deterministic choice {v1, v2, ...}."""
    values: list[Expr]

@dataclass
class TemporalUnary:
    op: str  # AG, AF, EF, EG, AX, EX, G, F, X
    operand: Expr

@dataclass
class TemporalBinary:
    op: str  # U
    left: Expr
    right: Expr

Expr = Union[IntLit, BoolLit, VarRef, NextRef, BinOp, UnaryOp,
             CaseExpr, SetExpr, TemporalUnary, TemporalBinary]


# --- Specifications ---

@dataclass
class SpecDecl:
    kind: str  # INVARSPEC, CTLSPEC, LTLSPEC, SPEC
    expr: Expr
    text: str = ""  # original text for display


# --- Top-level Model ---

@dataclass
class SmvModel:
    variables: dict[str, VarDecl] = field(default_factory=dict)
    defines: dict[str, Expr] = field(default_factory=dict)
    inits: dict[str, Expr] = field(default_factory=dict)
    nexts: dict[str, Expr] = field(default_factory=dict)
    fairness: list[Expr] = field(default_factory=list)
    specs: list[SpecDecl] = field(default_factory=list)


def get_domain(var_decl: VarDecl) -> list:
    """Return the list of all possible values for a variable."""
    vt = var_decl.var_type
    if isinstance(vt, BoolType):
        return [True, False]
    elif isinstance(vt, EnumType):
        return list(vt.values)
    elif isinstance(vt, RangeType):
        return list(range(vt.lo, vt.hi + 1))
    raise ValueError(f"Unknown var type: {vt}")


def expr_to_str(expr: Expr) -> str:
    """Convert an expression AST back to a readable string."""
    if isinstance(expr, IntLit):
        return str(expr.value)
    elif isinstance(expr, BoolLit):
        return "TRUE" if expr.value else "FALSE"
    elif isinstance(expr, VarRef):
        return expr.name
    elif isinstance(expr, NextRef):
        return f"next({expr.name})"
    elif isinstance(expr, UnaryOp):
        return f"!({expr_to_str(expr.operand)})"
    elif isinstance(expr, BinOp):
        return f"({expr_to_str(expr.left)} {expr.op} {expr_to_str(expr.right)})"
    elif isinstance(expr, CaseExpr):
        branches = "; ".join(
            f"{expr_to_str(c)} : {expr_to_str(v)}"
            for c, v in expr.branches
        )
        return f"case {branches} esac"
    elif isinstance(expr, SetExpr):
        return "{" + ", ".join(expr_to_str(v) for v in expr.values) + "}"
    elif isinstance(expr, TemporalUnary):
        return f"{expr.op} ({expr_to_str(expr.operand)})"
    elif isinstance(expr, TemporalBinary):
        return f"({expr_to_str(expr.left)} {expr.op} {expr_to_str(expr.right)})"
    return str(expr)
