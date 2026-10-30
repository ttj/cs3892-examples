# The LLM run behind 04_llm_vnnlib.py

- **Model:** Claude Haiku 4.5 (`claude-haiku-4-5`)
- **When:** 2026-10-30T15:58:17Z
- **How:** `claude -p --model claude-haiku-4-5 --tools "" --strict-mcp-config --no-session-persistence < prompt.txt`,
  run from an empty directory: no tools, no MCP servers, no files to read. One attempt; nothing
  was retried or edited.
- **Files:** `prompt.txt` is the prompt and `response.txt` the reply, both verbatim.

The script never calls a model: it checks the saved reply, so CI is deterministic.
