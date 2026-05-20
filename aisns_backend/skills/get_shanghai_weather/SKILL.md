---
name: Get Shenzhen Weather V3
skill_key: get_shenzhen_weather
description: Query Shenzhen weather for a given date and AM/PM.
instructions: Call by agent
requires:
  always: true
runner:
  kind: node_file
  target: scripts/run.js
---

# Get Guangzhou Weather

## Parameters

This skill accepts a JSON object as input params.

- `date` (string, optional)
  - Format: `YYYY-MM-DD`
  - Defaults to today's date if omitted.

- `ampm` (string, optional)
  - Values: `am` or `pm`
  - Also accepts: `morning`, `afternoon`, `上午`, `下午`
  - Defaults to `am` if omitted.

## How to use

1. Call `read_skill` with `skill_key: "get_shanghai_weather"` to read this document.
2. Then call `run_doc_skill` with `skill_key: "get_shanghai_weather"` and optional `params`.

Example:

```json
{
  "skill_key": "get_shanghai_weather",
  "params": {
    "date": "2026-02-12",
    "ampm": "am"
  }
}
```

## Output

The runner prints a JSON object to stdout.
