# B2: Throughput anomaly at prompt_len=3584

## The anomaly
| batch | reported_tok_s | preempted_seqs | kv_cache_util |
|---|---|---|---|
| 4  | 565.4  | 0  | 0.16 |
| 8  | 902.6  | 0  | 0.31 |
| 16 | 1311.4 | 0  | 0.62 |
| 24 | 1607.4 | 0  | 0.93 |
| 32 | 1384.0 | 7  | 0.97 |
| 48 | 1298.5 | 23 | 0.97 |

Throughput rises from batch 4→24, peaks at batch 24, then **falls**
at batch 32 and 48 - contradicting naive "more batch = more throughput."

## Mechanism
From B1, ~27 concurrent 4096-token sequences is the GPU's memory
ceiling. Batch 24 sits just under this ceiling (0 preemptions). Batch
32 and 48 exceed it, forcing the scheduler to preempt sequences
(evict/pause them to free KV-cache memory). Preempted sequences lose
progress and must resume later, wasting compute and idle time that
outweighs the throughput gained from a larger batch - so net throughput
drops as preemption count rises (7 at batch 32, 23 at batch 48).

## Proposed fix
Cap concurrent requests at ~24 for 4096-context workloads (via
max_num_seqs or admission control), avoiding the preemption regime
entirely. Predicted effect: sustained throughput near the batch-24
peak instead of degrading at higher nominal batch sizes.
(Note: the *reported* throughput number itself needs correction - see B3.)