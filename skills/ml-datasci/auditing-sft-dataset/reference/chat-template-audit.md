# Chat-template conformance audit — per-template ruleset

This reference defines the per-template conformance rules invoked by Step 2 of `auditing-sft-dataset`. The audit applies the target template's `apply_chat_template` function to every row and checks for the failure classes listed below.

## Generic checks (apply to every template)

1. **Render-success** — `apply_chat_template(row, add_generation_prompt=False)` does not raise
2. **No un-substituted Jinja** — rendered output contains no literal `{{` or `}}` substrings (would indicate the template engine swallowed a variable lookup error)
3. **No literal template tokens in content** — assistant / user / system content does not contain the special-token strings used by any *other* common template (see per-template lists below); cross-template token leakage indicates the dataset carries scaffolding from its origin template
4. **No empty content** — no role-block has empty content unless the template explicitly allows it (tool-call placeholders)
5. **Role discipline** — roles alternate per the template's contract; no two consecutive same-role turns unless the template documents support

## Per-template token allow-lists

For each target template, these tokens are EXPECTED in the rendered output. The same tokens appearing in *original content* (before rendering) usually indicate a mismatch — content was authored for a different template.

### Llama-3 family (`llama-3`, `llama-3.1`, `llama-3.2`)

Expected in rendered output:
- `<|begin_of_text|>`
- `<|start_header_id|>` / `<|end_header_id|>`
- `<|eot_id|>`
- `<|finetune_right_pad_id|>` (sometimes)

Forbidden inside row content:
- `<|im_start|>` / `<|im_end|>` (ChatML leakage)
- `[INST]` / `[/INST]` (Llama-2 / Mistral leakage)
- `<start_of_turn>` / `<end_of_turn>` (Gemma leakage)

### ChatML (`chatml`, `qwen-2`, `qwen-2.5`)

Expected in rendered output:
- `<|im_start|>` / `<|im_end|>`

Forbidden inside row content:
- `<|start_header_id|>` / `<|eot_id|>` (Llama-3 leakage)
- `[INST]` / `[/INST]` (Mistral leakage)
- `<start_of_turn>` / `<end_of_turn>` (Gemma leakage)

### Mistral-v3 (`mistral-v3`, `mistral-large`)

Expected in rendered output:
- `[INST]` / `[/INST]`
- `<s>` / `</s>` (BOS / EOS)
- `[AVAILABLE_TOOLS]` / `[/AVAILABLE_TOOLS]` (when tools are present)

Forbidden inside row content:
- `<|im_start|>` (ChatML leakage)
- `<|start_header_id|>` (Llama-3 leakage)

### Gemma-2 (`gemma-2`)

Expected in rendered output:
- `<start_of_turn>` / `<end_of_turn>`
- `<bos>`

Forbidden inside row content:
- `<|im_start|>` (ChatML leakage)
- `<|start_header_id|>` (Llama-3 leakage)
- `[INST]` (Mistral leakage)

Gemma-2 does NOT support `system` role natively; system-role messages are typically merged into the first user turn. Flag any row with a `system` role under a Gemma target.

## Per-template caveats

- **Llama-3.1 tool-calling** — assistant turns may legitimately contain `<|python_tag|>` for tool invocations; allow it
- **ChatML tool-use** — Qwen-2.5 uses `<tool_call>` JSON inside assistant content; allow it under the Qwen target
- **Mistral-v3 system** — Mistral has historically had ambiguous system-role support; document which variant of the template the audit assumed
- **Gemma-2 system** — explicitly flagged above; merge or fail per operator choice

## Output format for Step 2 findings

Each finding row:

```json
{
  "row_id": "...",
  "rule": "render-success" | "no-jinja" | "no-cross-template-tokens" | "no-empty-content" | "role-discipline",
  "detail": "<short description, e.g., 'assistant content contains <|im_start|>'>",
  "expected_template": "<target template name>",
  "evidence_span": {"offset": <int>, "length": <int>}
}
```

The evidence span points into the *original* row content (not the rendered output), so the user can navigate to the source for remediation.
