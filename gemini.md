# 📜 Project Constitution (gemini.md)

**LAW:** This document is the source of truth for all data schemas and architectural invariants.

## Data Schemas

### Product Schema (v1 — confirmed 2026-03-11)
```json
{
  "id": "string",
  "name": "string",
  "brand": "string",
  "category": "taska | cipo",
  "description": "string",
  "sizes": ["string"],
  "qty": "number",
  "images": ["relative-path.webp"]
}
```

**Categories:** `taska` (bags), `cipo` (shoes)
**Output format:** Static HTML/CSS (single-file, local)
**Audience:** Influencers / content creators
**Fields required:** sizes, description (no price data)

## Behavioral Rules
1. Never guess at business logic.
2. Logic must be deterministic (Layer 3 Tools).
3. Update Architecture SOPs before updating Tool code.

## Architectural Invariants
- Layer 1: SOPs in `architecture/`
- Layer 2: Reasoning in LLM
- Layer 3: Tools in `tools/`
