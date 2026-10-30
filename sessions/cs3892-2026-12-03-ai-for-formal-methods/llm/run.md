# The LLM runs behind session 26's examples

- **Model:** Claude Haiku 4.5 (`claude-haiku-4-5`)
- **When:** 2026-10-30T16:07:15Z
- **How:** `claude -p --model claude-haiku-4-5 --tools "" --strict-mcp-config --no-session-persistence < <prompt>`,
  each run from a new empty directory: no tools, no MCP servers, no files to read, no memory between
  calls. Nothing was retried, edited or selected.

| Task | Prompt | Reply | Tool's verdict, verbatim |
|---|---|---|---|
| English → LTL, four requirements of the running counter | `ltl_prompt.txt` | `ltl_response.txt` | checked by `01_llm_ltl.py` with NuSMV |
| A Lean proof, round 1 | `lean_prompt_round1.txt` | `lean_response_round1.txt` | `lean_check_round1.txt` |
| Round 2: the task, the first answer and Lean's error | `lean_prompt_round2.txt` | `lean_response_round2.txt` | `lean_check_round2.txt` |

Two rounds, as in HW4 Part 5's protocol; the second was also rejected, and the session stops there.
The scripts never call a model: they check the saved replies, so CI is deterministic.
