# HW2 — Temporal logic and model checking

Starters for [the HW2 handout](https://github.com/ttj/cs3892-fmstai-fall2026/blob/main/assignments/hw2.md).
**Out Thu Oct 1 · due Thu Oct 15, 11:59 p.m.**

These are **starters, not solutions.** No file here states a verdict the homework asks
you to predict, and the Part 2 model carries no specifications — the eight are yours.

| File | What it is | Part |
|---|---|---|
| `smv/agent_loop.smv` | a tool-using agent's control loop, with four properties `P1`–`P4`. **Predict their verdicts before you run it** | 1 |
| `smv/traffic_light.smv` | the vehicle-actuated traffic light. **Complete model, no specifications**; its variables are documented in the header | 2 |
| `smv/counter.smv` | the course's running counter (the class repo's `labs/running-example.md`), correct as given. **You plant the bug** | 3 |
| `smv/bmc_depth.smv` | two counters and a bug some number of steps deep, for the bound hunt | 4 |

Every file is plain NuSMV: finite types only, no nuXmv-only features. Each was run under
NuSMV 2.6.0, NuSMV 2.7.0 and nuXmv 2.2.0, and all three agree on every verdict.

## Run them

No install: [smvis](https://bit.ly/fmaiv_smvis) runs NuSMV in the browser on your own `.smv` files.
Part 1's `-r` count and all of Part 4 need NuSMV's command-line options, so use one of the
routes below for those.

The [`ttj/fmaiv`](https://github.com/ttj/fmaiv) Codespace has `NuSMV` preinstalled. Anywhere
else — Colab (put `!` in front of each line) or any Linux shell:

```bash
git clone --depth 1 https://github.com/ttj/cs3892-examples.git
mkdir -p nusmv
curl -sSLO https://nusmv.fbk.eu/distrib/NuSMV-2.6.0-linux64.tar.gz
tar -xzf NuSMV-2.6.0-linux64.tar.gz -C nusmv --strip-components=1
cp -r cs3892-examples/homework/hw2-temporal-logic-model-checking/smv hw2
nusmv/bin/NuSMV hw2/agent_loop.smv
```

With `NuSMV` on your `PATH`, from the folder holding the models:

```bash
NuSMV agent_loop.smv                      # check every property (BDDs)
NuSMV -r agent_loop.smv                   # ...and print the reachable-state count
NuSMV -bmc -bmc_length 5 bmc_depth.smv    # bounded model checking: runs of at most 5 steps
```

nuXmv takes the same command lines.

## Two things that trip people up

- **NuSMV does not always print verdicts in the order of the file** — every CTL result
  comes before every LTL one, for a start. Match each verdict to its property by the
  formula it prints.
- **A variable with no `init()` and no `next()` is a free input** — its value is chosen
  afresh at every step, *including the first*.
