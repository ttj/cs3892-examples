# cs3892-2026-10-06-ctl-and-buchi-automata

Session 12 — CTL and the path quantifiers; `EF` versus `AF`; why LTL and CTL are incomparable;
Büchi automata and the automata-theoretic view of LTL model checking.

| File | Shows | Verdicts | Tool |
|---|---|---|---|
| `smv/01_ctl_on_the_agent.smv` | the eight common CTL forms on session 11's agent, plus two LTL properties for the Büchi section | `EX` `EF` `EG` `AG EF` true · `AX` `AF` `AG` `AG AF` false · `G F del` false | NuSMV / nuXmv / **smvis** |
| `smv/02_ctl_until.smv` | `E [p U q]` and `A [p U q]` | true · false · true | NuSMV / nuXmv (smvis cannot parse the brackets) |
| `smv/03_ltl_vs_ctl.smv` | `F G p` true but `AF AG p` false; `AG EF` has no LTL form | false · true · true · false | NuSMV / nuXmv / smvis |
| `python/04_buchi_emptiness.py` | a Büchi automaton for ¬φ, the product with the agent, and the accepting-cycle search, by hand | `G F del` fails (lasso) · `G (del -> approved)` holds on the fixed agent, fails on the buggy one | Python |

Every SMV verdict was run under **NuSMV 2.6.0** and **nuXmv 2.2.0**; `01` and `03` also parse and
check in **smvis** ([bit.ly/fmaiv_smvis](https://bit.ly/fmaiv_smvis)), whose *Compose & Analyze* on
`G (F (del))` builds the same two-state automaton as `04` and finds an accepting cycle. The
notebook asserts everything, including that NuSMV agrees with `04`.
