#!/usr/bin/env python3
"""Draw every transition-system example as a state-machine graph.

THE RULE (lint_examples.sh enforces it): any example that is a transition
system and is shown in slides or Colab gets a graph of its state machine. When
the model has data variables, every edge carries its GUARD and its UPDATE, as
`guard / update`, so the example reads visually and not only as code.

This script holds the Graphviz source for each figure, renders it with `dot`
into sessions/<session>/figures/, and is the one place to edit a drawing.

    python3 scripts/draw_models.py          # re-render every figure

Homework starters are deliberately NOT drawn: HW2 Part 1 asks students to
derive the transition relation themselves.
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HEAD = '''digraph G {
  rankdir=LR; bgcolor="white"; pad=0.25; nodesep=0.55; ranksep=0.8;
  node [shape=box, style="rounded,filled", fillcolor="white", color="#1f2430",
        fontname="Helvetica", fontsize=14, penwidth=1.6, margin="0.18,0.08"];
  edge [color="#1f2430", fontname="Helvetica", fontsize=12, penwidth=1.3, arrowsize=0.8];
  start [shape=point, width=0.12, color="#2f55d4", fillcolor="#2f55d4", label=""];
'''

FIG = {
    # One control location; the data variable x carries the state.
    "counter": '''
  label="the running counter (labs/running-example.md) - edges are  guard / update";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  count [label="x"];
  start -> count [label="x := 0"];
  count:n -> count:n [label="x < 10 / x := x + 1", color="#1b7a43", fontcolor="#1b7a43"];
  count:s -> count:s [label="x >= 10 / x := 0", color="#c0392b", fontcolor="#c0392b"];
''',
    "add2": '''
  label="the add-2 counter - no guard, no reset; reachable x: 0, 2, 4, ...";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  count [label="x"];
  start -> count [label="x := 0"];
  count -> count [label="true / x := x + 2"];
''',
    "thermostat": '''
  label="the thermostat - each step heats or cools (a nondeterministic choice); property: t < 30";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  heat [label="t"];
  start -> heat [label="t := 20"];
  heat:n -> heat:n [label="t := t + 3"];
  heat:s -> heat:s [label="t := t - 1"];
''',
    "modes_efsm": '''
  label="two modes and a button - press is a free input; edges are  guard / update";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  off; on [fillcolor="#e3e9fb", color="#2f55d4"];
  start -> off [label="x := 0"];
  off -> off [label="!press / x held"];
  off -> on  [label="press / x held"];
  on -> on   [label="!press & x < 10 / x := x + 1", color="#1b7a43", fontcolor="#1b7a43"];
  on -> off  [label="press | x >= 10 / x := 0", color="#c0392b", fontcolor="#c0392b"];
''',
    "mutex": '''
  label="process a (b is the mirror image, with move = 2). When the guard is false, a stays put.";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  idle; trying; critical [fillcolor="#e3e9fb", color="#2f55d4"];
  start -> idle;
  idle -> trying [label="move = 1"];
  trying -> critical [label="move = 1 & b != critical"];
  critical -> idle [label="move = 1"];
''',
    "three_state": '''
  label="F G p is true; AF AG p is false; AG EF s2 is true";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  s0 [label="s0 : p", fillcolor="#e3e9fb", color="#2f55d4"];
  s1 [label="s1 : !p", fillcolor="#fbe4e4", color="#c0392b"];
  s2 [label="s2 : p", fillcolor="#e3e9fb", color="#2f55d4"];
  start -> s0; s0 -> s0; s0 -> s1; s1 -> s2; s2 -> s2;
''',
    "agent": '''
  plan; ask;
  act   [label="act - del", fillcolor="#e3e9fb", color="#2f55d4"];
  abort [fillcolor="#eeeeea"];
  done;
  start -> plan;
  plan -> ask; plan -> abort;
  ask -> act [label="yes / approved := true", fontcolor="#1b7a43"];
  ask -> abort [label="no"];
  act -> done [label="approved := false"]; abort -> done;
  done -> plan [constraint=false];
''',
}
FIG["agent_buggy"] = FIG["agent"] + '''
  plan -> act [label="BUG: shortcut, no one asked", color="#c0392b", fontcolor="#c0392b", style=dashed];
'''
FIG["agent_fixed"] = FIG["agent"]

# Which session folder holds which figure.
WHERE = {
    "cs3892-2026-09-22-smt-theories-and-bounded-reachability": ["thermostat", "modes_efsm"],
    "cs3892-2026-09-24-inductive-invariants-and-smv": ["counter", "add2"],
    "cs3892-2026-09-29-project-lightning-talks": ["counter", "add2"],
    "cs3892-2026-10-01-linear-temporal-logic": ["counter", "mutex", "agent_buggy", "agent_fixed"],
    "cs3892-2026-10-06-ctl-and-buchi-automata": ["agent", "three_state"],
}

if __name__ == "__main__":
    for session, figs in WHERE.items():
        out = ROOT / "sessions" / session / "figures"
        out.mkdir(exist_ok=True)
        for f in figs:
            src = HEAD + FIG[f] + "}\n"
            svg = subprocess.run(["dot", "-Tsvg"], input=src, capture_output=True, text=True, check=True).stdout
            (out / f"{f}.svg").write_text(svg)
            print(f"  {session}/figures/{f}.svg")
