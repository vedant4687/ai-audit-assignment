# B1: KV-cache capacity calculation

## KV cache bytes per token
Formula: 2 (K and V) × num_layers × KV_heads × head_dim × bytes_per_element

= 2 × 28 × 8 × 128 × 2 (fp16)
= 114,688 bytes/token (112 KiB/token)

Note: uses KV_heads (8), not Q attention heads (24) — this model uses
GQA (grouped-query attention), where multiple query heads share KV heads.

## Max concurrent 4096-token sequences
- Usable GPU memory: 24 GB × 0.92 = 22.08 GB
- Minus model weights: 4.2B params × 2 bytes (fp16) = 8.4 GB
- Minus non-KV overhead: 1.6 GB (given)
- Available for KV cache: 22.08 - 8.4 - 1.6 = 12.08 GiB

- 12.08 GiB ≈ 12,970,800,662 bytes
- ÷ 114,688 bytes/token ≈ 113,096 tokens total capacity
- ÷ 4096 tokens/sequence ≈ 27.6 → **~27 concurrent sequences**

## Verification against bench_log.csv
At prompt_len=3584 + gen_len=512 (= 4096 context):
- batch=24: kv_cache_util=0.93, preempted_seqs=0 — fits cleanly
- batch=32: kv_cache_util=0.97, preempted_seqs=7 — exceeds ceiling
- batch=48: kv_cache_util=0.97, preempted_seqs=23 — heavy overflow

Prediction (~27) matches the observed transition point closely.