## Day 1 - 04/09/26
- Received assignment, set up repo structure
- About to read REPORT_v0.md and fertility.py

## Day 1 (continued)
- Set up repo, got starter_kit running
- Reproduced baseline: eng fertility 1.27, hin fertility 7.45, ratio 5.89x
- Matches REPORT_v0.md exactly — confirms script runs as reported
- Next: testing whether .lower() call distorts the eng/hin comparison

## Day 1 (continued)
- Hypothesis: .lower() in analyze() distorts eng/hin comparison since 
  Hindi has no case-folding effect
- Ran test_lowercase.py comparing fertility with/without lowercasing
- Result: eng fertility 1.2293 (no lower) -> 1.2652 (lower), +2.94% 
  distortion. hin fertility unchanged (7.44845 both ways).
- Conclusion: confirmed bug, but small magnitude — doesn't explain 
  the bulk of the 5.89x gap. Direction: makes eng LOOK slightly worse 
  than it is, so ratio is very slightly overstated (~3%), not the main story.

## Day 1 (continued)
- Hypothesis: split(" ") vs split() word-counting bug could distort comparison
- Ran test_wordsplit.py comparing naive split(" ") vs whitespace split()
- Result: eng 79->78 words (1 line w/ double space), hin 62->61 words 
  (1 line w/ double space). Same magnitude bug in both languages.
- Conclusion: real minor bug (double-space handling), but affects both 
  languages symmetrically -> negligible effect on eng/hin RATIO. 
  Not a driver of the 5.89x gap.

## Day 1 (continued) - KEY FINDING
- Hypothesis: report's claim that Hindi's high fertility is a "script 
  property, not tokenizer property" is testable by swapping tokenizers
- Ran fertility.py with hf:xlm-roberta-base instead of gpt2, same corpus
- Result: hin/eng ratio dropped from 5.89x (gpt2) to 1.10x (xlm-roberta)
- Conclusion: report's root-cause claim is FALSIFIED. The gap is 
  ~84% explained by GPT-2's English-centric vocabulary, not by 
  Hindi's script complexity. This is the core conceptual bug in 
  REPORT_v0's Section 1.

## Day 1 (continued)
- Hypothesis: random.seed(1337) might be masking some non-determinism 
  or sampling that affects the numbers
- Ran: Select-String -Path fertility.py -Pattern "random\."
- Result: only ONE match — the import/seed line itself. `random` module 
  is never called anywhere else in the script.
- Conclusion: confirmed harmless — dead code with zero effect on 
  fertility/tok-per-char numbers. This is the "looks suspicious but is 
  actually fine" item required by the assignment. Flagging with evidence, 
  not flagging as a bug.

## Day 2 - 05/09/26
- Part A1: built real multilingual eval corpus using FLORES+ 
  (openlanguagedata/flores_plus, dev split)
- Languages: English (eng_Latn), Hindi (hin_Deva), Kannada (kan_Knda), 
  Tamil (tam_Taml) - satisfies "Hindi + 2 Dravidian languages" requirement
- 997 parallel sentences per language, same content across all 4 
  (news/wiki-style text, FLORES's standard domain)
- Hit blockers: facebook/flores and Muennighoff/flores200 were 
  gated/deprecated; switched to openlanguagedata/flores_plus, 
  required HF login (browser OAuth) to access
- Corpus saved to partA/corpus/{eng,hin,kan,tam}.txt

## Day 2 (continued) - A3 corrected analysis
- Ran corrected_analysis.py: 2 tokenizers (gpt2, xlm-roberta-base) x 
  4 denominators (tok/word, tok/char, tok/byte, tok/sentence) x 4 
  languages, using full FLORES+ corpus (997 sentences each)
- Results confirm and STRENGTHEN the A2 finding: gpt2 shows hin/kan/tam 
  as 7-15x worse than eng; xlm-roberta shows all three as a tight 
  1.26-1.37x range
- Kannada and Tamil are punished even harder than Hindi under gpt2 
  (13.59x, 15.43x vs 7.44x) - consistent with "less-represented script 
  in tokenizer training data" being the driver, not language difficulty
- Chose tok/sentence as the primary decision metric: FLORES is parallel 
  (same content across languages), so tokens-per-sentence directly 
  measures "cost to convey the same amount of meaning" - the actual 
  quantity that matters for serving cost, unlike tok/word or tok/char 
  which depend on language-specific word/character conventions

## Day 2 (continued) - A4 memo written
- Synthesized A2 (conceptual bug found) + A3 (corrected numbers) into 
  a 1-page recommendation memo
- Core message: 6-15x cost estimate was a tokenizer artifact, not a 
  language property; real expected cost with proper tokenizer is ~1.3x
- Flagged FLORES's formal/news register as the key caveat requiring 
  production validation

 ## Day 2 (continued) - B1: KV-cache math
- Computed KV cache bytes/token = 2 * 28 layers * 8 KV_heads * 128 head_dim 
  * 2 bytes (fp16) = 114,688 bytes/token (112 KiB/token)
- Available memory for KV cache = (24GB * 0.92) - 8.4GB weights - 1.6GB 
  overhead = 12.08 GiB
- Predicted max concurrent 4096-token sequences = ~27
- Verified against bench_log.csv: batch=24 (prompt 3584+gen 512=4096 
  context) runs clean (kv_util=0.93, 0 preemptions); batch=32 already 
  shows preemptions (7) and near-saturated kv_util (0.97). Matches 
  predicted ceiling closely.

## Day 2 (continued) - B2/B3: throughput anomaly + goodput miscalculation

 ### B2 - Anomaly at prompt_len=3584 sweep:
- Throughput (reported_tok_s) climbs batch 4->24 (565 -> 1607), but 
  DROPS at batch 32 (1384) and batch 48 (1298), even though batch size 
  increases
- Mechanism: batch 24 = 0 preempted_seqs, kv_cache_util=0.93 (near but 
  under B1's ~27-sequence capacity ceiling). Batch 32 = 7 preemptions, 
  kv_cache_util=0.97 (over ceiling). Batch 48 = 23 preemptions (nearly 
  half the batch), kv_cache_util=0.97.
- Once concurrent sequences exceed the KV-cache memory ceiling (~27, 
  from B1), the scheduler must preempt (evict/pause) sequences to free 
  memory, causing recomputation/idle time that costs more than the 
  extra batch size gains -> throughput falls instead of rising
- Proposed fix: cap concurrent requests at ~24-27 for 4096-context 
  workloads (e.g. via max_num_seqs or admission control), or use a 
  smaller max_model_len / shorter context budget to fit more concurrent 
  sequences without triggering preemption. Predicted effect: capping 
  at batch~24 avoids the 1384/1298 tok/s regression, sustaining closer 
  to the observed peak (~1607 tok/s reported-metric, though see B3 for 
  why even that number needs correction)

### B3 - reported_tok_s is NOT goodput:
- Verified formula: reported_tok_s = (prompt_len + gen_len) * num_requests 
  / wall_clock_s -- e.g. batch=16: (3584+512)*16/49.97 = 1311.5, matches 
  logged 1311.4 exactly
- This means reported_tok_s counts PREFILL (prompt) tokens as if they 
  were generated output, massively inflating the number, since prefill 
  is fast/parallel and decode (actual generation) is the real bottleneck
- Computed true goodput for batch=24 two independent ways:
  Method 1 (from output): (24*512)/61.16 = 200.9 tok/s
  Method 2 (from itl_ms_p50): 24 * (1000/96.07) = 249.8 tok/s
  Both land ~200-250 tok/s -- nowhere near reported 1607.4
- Conclusion: REPORT_v0's claims ("longer prompts give better 
  throughput", "batch 48 -> ~3200 tok/s") are both artifacts of this 
  same metric confusion (counting prefill+decode as one throughput 
  number) compounded with ignoring the preemption ceiling found in B2. 
  Corrected: true goodput at batch 24 is ~200-250 tok/s, and batch 48 
  likely has LOWER goodput than batch 24, not higher, due to heavy 
  preemption (23/48 sequences preempted)

## Day 2 (continued) - B4: confirmation metric
- Reasoned through which single serving-stack metric would confirm 
  the B2 preemption mechanism, rather than running a new experiment 
  (no live serving stack access to pull real-time metrics)
- Answer: preempted_seqs tracked per-step, cross-referenced with 
  kv_cache_util and itl_ms_p50 at the same timestamps -- expect 
  kv_cache_util climbing toward ~0.95-0.97 right before preemption 
  spikes, and itl_ms_p50 jumping above steady-state (~90-100ms) for 
  affected sequences immediately after a preemption event
- Saved as partB/b4_confirmation_metric.md

## Day 2 (continued) - wrap-up
- Organized final B1-B4 answers into partB/ as separate files 
  (b1_kv_cache_math.md, b2_throughput_anomaly.md, 
  b3_goodput_correction.md, b4_confirmation_metric.md) — previously 
  these calculations only existed as notebook entries, moved clean 
  writeups into partB/ per the required repo structure
- Confirmed partA/ (corpus_notes.md, corrected_analysis.py, 
  recommendation_memo.md) and partC/ (memo.md) are complete
- Remaining: AI_USAGE.md, final review pass, defense prep

## Day 2 (continued) - B3 re-verification
- Double-checked reported_tok_s formula against a second row (batch=24) 
  in addition to batch=16 - both match the formula 
  (prompt_len+gen_len)*num_requests/wall_clock_s almost exactly, 
  confirming this isn't a coincidence at one data point
- Noted GiB vs GB ambiguity in B1's memory conversion as a caveat to 
  be ready to discuss in defense - doesn't change the ~27 sequence 
  conclusion meaningfully

## Day 2 (continued) - Part C memo
- Drafted the Part C decision memo: chose prompt-engineering-only 
  over SFT or a small rewriter model, given constraints (1 A100/2 weeks, 
  1 reviewer 10h/week Hindi+Kannada only, 3-week launch, no API budget)
- Reasoning: SFT/rewriter both need per-language review of training 
  data, but only 2 of 6 languages have any native review coverage; 
  prompt-engineering is fastest to iterate and cheapest to re-review
- Included labeled assumptions, back-of-envelope reviewer-hour and 
  GPU-usage arithmetic, a numeric success threshold, a kill criterion, 
  and a day-1 experiment
- Saved as partC/memo.md

## Day 2 (continued) - repo cleanup
- Renamed folders for consistency: "part c" -> partC, part-a -> partA, 
  part-b -> partB
- Created partA/a2_script_audit.md as a dedicated writeup of the A2 
  bug audit (previously the findings only lived in NOTEBOOK.md and 
  briefly in recommendation_memo.md) — separated process log from 
  final deliverable per the repo structure
- Caught a real mistake: partC/memo.md was initially saved empty (0 
  bytes), then on the first fix attempt it accidentally ended up with 
  the A2 audit content instead of the Part C memo (both files were 
  2041 bytes — a giveaway). Reviewed and corrected by re-pasting the 
  correct Part C memo content; verified via file size difference and 
  a content spot-check (Get-Content -TotalCount 3)


  -----