---
type: regex
target:
  source: file
  path: pricing/legacy_v1.py
---
(?s)^def legacy_total\(value\):\n    return value\n$
