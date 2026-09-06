## B4: Metric to confirm the preemption mechanism

The single most direct metric to pull would be **`preempted_seqs`
itself, tracked over time (per-step, not just a run-level total)**,
cross-referenced with **`kv_cache_util`** at the same timestamps. If
the preemption-driven mechanism from B2 is correct, we'd expect to see
`kv_cache_util` climb toward its ceiling (~0.95-0.97) right before each
spike in preemption events, and each preemption event should correlate
with a visible stall or spike in `itl_ms_p50` (inter-token latency) for
the affected sequences immediately afterward - since a preempted
sequence has to wait and then resume, its per-token latency during
that window should jump well above the steady-state ~90-100ms seen in
the batch=24 row. Seeing this tight time-correlation (memory pressure
-> preemption -> localized latency spike -> reduced aggregate goodput)
would confirm the mechanism; if preemptions occurred without any
accompanying latency/goodput impact, that would undermine this
explanation and point to a different cause.