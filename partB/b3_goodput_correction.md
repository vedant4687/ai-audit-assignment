# B3: Goodput vs reported throughput

## The bug
`reported_tok_s` = (prompt_len + gen_len) × num_requests ÷ wall_clock_s

Verified against two independent rows:
- batch=16: (3584+512)×16 ÷ 49.97 = 1311.5 ≈ logged 1311.4
- batch=24: (3584+512)×24 ÷ 61.16 = 1607.3 ≈ logged 1607.4

This confirms the formula holds consistently, not just at one data
point. This counts prefill (prompt-reading) tokens as if they were
generated output. Prefill is fast/parallel; decode (actual generation)
is the real bottleneck. Mixing them inflates the reported number.

## Corrected goodput (batch=24, prompt_len=3584)

**Method 1 — from generated output:**
(24 × 512) ÷ 61.16 = 200.9 tok/s

**Method 2 — from decode latency (itl_ms_p50):**
24 × (1000 ÷ 96.07) = 249.8 tok/s

Both land ~200-250 tok/s — far below the reported 1607.4 tok/s.

## What the report should have said
True generation goodput at batch 24 is ~200-250 tok/s, not 1607 tok/s.
The claim "batch 48 → ~3200 tok/s" is doubly wrong: it extrapolates
from an inflated metric, and ignores that batch 48 already shows heavy
preemption (23/48 sequences) — meaning real goodput at batch 48 is
likely *lower* than at batch 24, not higher.