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
# Automata (session 13): circles, accepting states doubled, edges labelled by
# the letter read -- the letter IS the guard.
AUT = '''
  node [shape=circle, fixedsize=true, width=0.62, margin=0];
  edge [fontname="Courier", fontsize=14];
'''
ACC = 'shape=doublecircle, fillcolor="#e3e9fb", color="#2f55d4"'
FIG.update({
    "dfa_ends_d": AUT + f'''
  label="END_D. Finite words: accept if the run ENDS in q1 -- (d|n)* d.\\nInfinite words (Buchi): accept if q1 comes back INFINITELY OFTEN -- G F d.";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  q0; q1 [{ACC}];
  start -> q0;
  q0 -> q0 [label="n"]; q0 -> q1 [label="d"];
  q1 -> q1 [label="d"]; q1 -> q0 [label="n"];
''',
    "dfa_even_d": AUT + f'''
  label="EVEN_D - an even number of d (a parity bit)";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  e [{ACC}]; o;
  start -> e;
  e -> e [label="n"]; e -> o [label="d"];
  o -> o [label="n"]; o -> e [label="d"];
''',
    "product_end_even": AUT + f'''
  label="END_D x EVEN_D, run in lockstep: accept when BOTH accept -- ends with d, and an even number of d";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  node [width=0.9];
  q0e [label="q0, e"]; q1o [label="q1, o"]; q0o [label="q0, o"]; q1e [label="q1, e", {ACC}];
  start -> q0e;
  q0e -> q0e [label="n"]; q0e -> q1o [label="d"];
  q1o -> q0o [label="n"]; q1o -> q1e [label="d"];
  q0o -> q0o [label="n"]; q0o -> q1e [label="d"];
  q1e -> q0e [label="n"]; q1e -> q1o [label="d"];
''',
    "nfa_ends_d": AUT + f'''
  label="An NFA for (d|n)* d, END_D's language: on a d it may GUESS that this is the last letter.\\nThe sets of states its runs can be in are {{p0}} and {{p0,p1}} -- END_D's q0 and q1.";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  p0; p1 [{ACC}];
  start -> p0;
  p0 -> p0 [label="d, n"]; p0 -> p1 [label="d  (the guess)"];
''',
    "nfa_second_last": AUT + f'''
  label="An NFA for (d|n)* d (d|n): it GUESSES which d is second-to-last. Accept if SOME run ends in p2.";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  p0; p1; p2 [{ACC}];
  start -> p0;
  p0 -> p0 [label="d, n"]; p0 -> p1 [label="d  (the guess)"]; p1 -> p2 [label="d, n"];
''',
    "dfa_second_last": AUT + f'''
  label="The subset construction: DFA states are SETS of NFA states. 4 = 2^2 states, all of them needed.";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  node [width=1.05, fontsize=12];
  a [label="{{p0}}"]; b [label="{{p0,p1}}"]; c [label="{{p0,p1,p2}}", {ACC}]; e [label="{{p0,p2}}", {ACC}];
  start -> a;
  a -> a [label="n"]; a -> b [label="d"];
  b -> c [label="d"]; b -> e [label="n"];
  c -> c [label="d"]; c -> e [label="n"];
  e -> b [label="d"]; e -> a [label="n"];
''',
    "nba_fg_n": AUT + f'''
  label="F G n - eventually no more deletes. The jump to q1 GUESSES when; a d in q1 has no move, so that guess dies.\\nNo deterministic Buchi automaton accepts this language [Landweber 1969].";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  q0; q1 [{ACC}];
  start -> q0;
  q0 -> q0 [label="d, n"]; q0 -> q1 [label="n  (the guess)"]; q1 -> q1 [label="n"];
''',
    "dba_even_pos": AUT + f'''
  label="d at every even position (0, 2, 4, ...): omega-regular, deterministic -- and no LTL formula says it [Wolper 1983]";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  e [{ACC}]; o;
  start -> e;
  e -> o [label="d"]; o -> e [label="d, n"];
''',
})

FIG["mutex_composition"] = '''
  label="S = M1 || M2, interleaved: a state is a PAIR (M1's state, M2's state). Each module alone has 2 states; S has 2 x 2 = 4.\\nThe two dashed moves are blocked by the guard, so (crit, crit) is never reached: mutual exclusion is a reachability fact.";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  ii [label="idle, idle"];
  ci [label="crit, idle", fillcolor="#e3e9fb", color="#2f55d4"];
  ic [label="idle, crit", fillcolor="#e3e9fb", color="#2f55d4"];
  cc [label="crit, crit", fillcolor="#fbe4e4", color="#c0392b", style="rounded,filled,dashed"];
  start -> ii;
  ii -> ci [label="M1 enters"]; ci -> ii [label="M1 exits"];
  ii -> ic [label="M2 enters"]; ic -> ii [label="M2 exits"];
  ci -> cc [label="M2 blocked", style=dashed, color="#c0392b", fontcolor="#c0392b"];
  ic -> cc [label="M1 blocked", style=dashed, color="#c0392b", fontcolor="#c0392b"];
'''
# Session 14: equivalence, simulation, bisimulation.
BLUE = 'fillcolor="#e3e9fb", color="#2f55d4"'
FIG.update({
    "vending_late": '''
  label="LATE: takes the coin, THEN lets you choose. From `paid` both drinks are still possible.";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  idle; paid [''' + BLUE + ''']; coffee; tea;
  start -> idle;
  idle -> paid [label="coin"];
  paid -> coffee [label="choose"]; paid -> tea [label="choose"];
  coffee -> idle; tea -> idle;
''',
    "vending_early": '''
  label="EARLY: commits to a drink AS it takes the coin. Both paid states show `paid`.\\nSame traces as LATE -- no LTL formula tells them apart -- but not bisimilar.";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  idle; paid_c [label="paid_c\\n(shows: paid)", ''' + BLUE + ''']; paid_t [label="paid_t\\n(shows: paid)", ''' + BLUE + ''']; coffee; tea;
  start -> idle;
  idle -> paid_c [label="coin"]; idle -> paid_t [label="coin"];
  paid_c -> coffee; paid_t -> tea;
  coffee -> idle; tea -> idle;
''',
    "fair_jams": '''
  label="FAIR and JAMS simulate EACH OTHER -- FAIR's paid can wait as long as stuck does -- and are still NOT bisimilar:\\nno state of FAIR behaves like stuck, which can never serve.";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  subgraph cluster_f { label="FAIR"; fontname="Helvetica"; color="#bbbbbb";
    f_idle [label="idle"]; f_paid [label="paid", ''' + BLUE + ''']; f_coffee [label="coffee"];
    f_idle -> f_paid [label="coin"]; f_paid -> f_paid [label="wait"]; f_paid -> f_coffee [label="serve"]; f_coffee -> f_idle; }
  subgraph cluster_j { label="JAMS"; fontname="Helvetica"; color="#bbbbbb";
    j_idle [label="idle"]; j_ok [label="ok\\n(shows: paid)", ''' + BLUE + ''']; j_stuck [label="stuck\\n(shows: paid)", fillcolor="#fbe4e4", color="#c0392b"]; j_coffee [label="coffee"];
    j_idle -> j_ok [label="coin"]; j_idle -> j_stuck [label="coin"]; j_ok -> j_ok [label="wait"]; j_ok -> j_coffee [label="serve"];
    j_stuck -> j_stuck [label="wait"]; j_coffee -> j_idle; }
  start -> f_idle; start2 [shape=point, width=0.12, color="#2f55d4", fillcolor="#2f55d4", label=""]; start2 -> j_idle;
''',
    "ends_d3": AUT + f'''
  label="END_D3: three states for 'ends with d'. q0 and q2 are bisimilar -- same acceptance, same moves into the same classes --\\nso partition refinement merges them, and the quotient is the two-state END_D of session 13.";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  q0 [fillcolor="#eeeeea"]; q2 [fillcolor="#eeeeea"]; q1 [{ACC}];
  start -> q0;
  q0 -> q2 [label="n"]; q0 -> q1 [label="d"];
  q2 -> q0 [label="n"]; q2 -> q1 [label="d"];
  q1 -> q1 [label="d"]; q1 -> q2 [label="n"];
''',
    "agent_abstraction": '''
  label="The agent (five states) and its abstraction under h: act -> del, everything else -> quiet. An abstract edge h(s) -> h(t) for every\\nagent edge s -> t, so the abstraction SIMULATES the agent. The dashed path del, quiet, del is spurious: the agent has no such run.";
  labelloc=b; fontname="Helvetica"; fontsize=12;
  subgraph cluster_c { label="the agent"; fontname="Helvetica"; color="#bbbbbb";
    plan; ask; act [label="act - del", ''' + BLUE + ''']; abort; done;
    plan -> ask; plan -> abort; ask -> act [label="yes"]; ask -> abort [label="no"]; act -> done; abort -> done; done -> plan [constraint=false]; }
  subgraph cluster_a { label="the abstraction"; fontname="Helvetica"; color="#bbbbbb";
    quiet; del [''' + BLUE + '''];
    quiet -> quiet; quiet -> del [color="#c0392b", style=dashed]; del -> quiet [color="#c0392b", style=dashed]; }
  start -> plan; start3 [shape=point, width=0.12, color="#2f55d4", fillcolor="#2f55d4", label=""]; start3 -> quiet;
''',
})

FIG["agent_buggy"] = FIG["agent"] + '''
  plan -> act [label="BUG: shortcut / approved := false", color="#c0392b", fontcolor="#c0392b", style=dashed];
'''
FIG["agent_fixed"] = FIG["agent"]

# Which session folder holds which figure.
WHERE = {
    "cs3892-2026-09-22-smt-theories-and-bounded-reachability": ["thermostat", "modes_efsm"],
    "cs3892-2026-09-24-inductive-invariants-and-smv": ["counter", "add2"],
    "cs3892-2026-09-29-project-lightning-talks": ["counter", "add2"],
    "cs3892-2026-10-01-linear-temporal-logic": ["counter", "mutex", "agent_buggy", "agent_fixed"],
    "cs3892-2026-10-06-ctl-and-buchi-automata": ["agent", "three_state"],
    "cs3892-2026-10-08-regular-languages-and-buchi-automata": ["dfa_ends_d", "dfa_even_d", "product_end_even",
        "nfa_ends_d", "nfa_second_last", "dfa_second_last", "mutex_composition", "nba_fg_n", "dba_even_pos", "agent"],
    "cs3892-2026-10-13-equivalence-simulation-and-bisimulation": ["vending_late", "vending_early", "fair_jams",
        "ends_d3", "agent_abstraction"],
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
