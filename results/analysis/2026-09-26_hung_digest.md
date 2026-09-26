# Results Digest for the Paper, 26 September 2026 (BackdoorBench normalization)

**Author:** Dang Khanh Hung. **Source files:** `results/raw/all_subsets/finetune_s42_bb_n6.json`, `finetune_s0_bb_n6.json`. Every number below was computed from those two files by script, not typed from memory. If a number in the paper disagrees with this page, the JSON wins and this page is wrong; tell me.

Two repairs. **s42**: fine-tuned under the legacy normalization (std 0.2023, 0.1994, 0.2010), seed 42. **s0**: fine-tuned under BackdoorBench's normalization (std 0.247, 0.243, 0.261), seed 0. Both evaluated under BackdoorBench's normalization. The two therefore differ in seed and in training normalization; say so in the paper.

Share order (greedy repair-aware): shard 3 (0.4774), 4 (0.2429), 2 (0.2111), 1 (0.0644), 0 (0.0030), 5 (0.0013).

## 1. Endpoints

| | s42 ASR | s42 CA | s0 ASR | s0 CA |
|---|---|---|---|---|
| Infected (full rollback, both seeds identical) | 95.06 | 91.33 | 95.06 | 91.33 |
| Repaired (k=0) | 0.81 | 93.18 | 1.13 | 93.51 |

The infected numbers match BackdoorBench's published values for this checkpoint. Section III-A may now say so.

## 2. Single shard (k=1)

| Shard | Layer | share | s42 ASR | s42 CA | s0 ASR | s0 CA |
|---|---|---|---|---|---|---|
| 0 | conv1 | 0.30% | 0.81 | 92.83 | 1.12 | 93.34 |
| 1 | layer1 | 6.44% | 0.91 | 90.24 | 1.50 | 92.18 |
| 2 | layer2 | 21.11% | 5.36 | 87.88 | 4.57 | 89.90 |
| 3 | layer3 | 47.74% | 0.40 | 86.76 | 0.39 | 86.78 |
| 4 | layer4 | 24.29% | 3.96 | 90.85 | 16.40 | 89.36 |
| 5 | linear | 0.13% | 1.09 | 93.15 | 1.51 | 93.52 |

Maximum single-shard ASR: 5.36 (s42), 16.40 (s0). Shard 3, the largest share, gives the lowest ASR in both.

## 3. Greedy repair-aware path (shards added in share order 3, 4, 2, 1, 0, 5)

| k | shards | s42 ASR | s42 CA | s0 ASR | s0 CA |
|---|---|---|---|---|---|
| 1 | {3} | 0.40 | 86.76 | 0.39 | 86.78 |
| 2 | {3,4} | 1.63 | 90.74 | 11.34 | 90.49 |
| 3 | {2,3,4} | 56.42 | 89.04 | 81.11 | 89.93 |
| 4 | {1,2,3,4} | 92.30 | 91.13 | 95.82 | 91.20 |
| 5 | {0,1,2,3,4} | 93.41 | 91.54 | 93.50 | 91.55 |
| 6 | all | 95.06 | 91.33 | 95.06 | 91.33 |

Crosses 50% at k=3 in both. At k=4 the CA is 2.05 (s42) and 2.31 (s0) points below the repaired model and within 0.2 of the infected model's own 91.33. **This k=4 row is the stealth headline.**

## 4. Architectural path (index order 0, 1, 2, ...)

| k | s42 ASR | s42 CA | s0 ASR | s0 CA |
|---|---|---|---|---|
| 1 | 0.81 | 92.83 | 1.12 | 93.34 |
| 2 | 0.92 | 89.86 | 1.17 | 92.19 |
| 3 | 4.63 | 90.97 | 5.70 | 90.94 |
| 4 | 3.31 | 88.53 | 4.82 | 86.12 |
| 5 | 93.41 | 91.54 | 93.50 | 91.55 |

Crosses 50% at k=5 in both.

## 5. Exact mean over all C(6,k) subsets (replaces the five random draws)

| k | n | s42 mean ASR | s42 mean CA | s0 mean ASR | s0 mean CA |
|---|---|---|---|---|---|
| 1 | 6 | 2.09 | 90.28 | 4.25 | 90.85 |
| 2 | 15 | 5.23 | 87.56 | 12.54 | 88.42 |
| 3 | 20 | 13.82 | 86.02 | 26.55 | 86.96 |
| 4 | 15 | 32.05 | 86.10 | 44.72 | 86.84 |
| 5 | 6 | 60.63 | 88.10 | 67.62 | 88.31 |

Use this as the "random" line in Fig. 3 and say "mean over all C(6,k) subsets". It is exact, so the sampling-variance discussion of the old draws is no longer needed.

## 6. Best subset per k (exhaustive adversary)

| k | s42 subset | s42 ASR | s42 CA | s0 subset | s0 ASR | s0 CA |
|---|---|---|---|---|---|---|
| 1 | {2} | 5.36 | 87.88 | {4} | 16.40 | 89.36 |
| 2 | {2,4} | 32.96 | 81.03 | {2,4} | 66.56 | 85.23 |
| 3 | {1,2,4} | 64.39 | 85.00 | {1,2,4} | 92.80 | 86.77 |
| 4 | {1,2,3,4} | 92.30 | 91.13 | {1,2,4,5} | 96.07 | 81.79 |
| 5 | {1,2,3,4,5} | 94.53 | 90.81 | {1,2,3,4,5} | 96.49 | 90.80 |

## 7. Which shards matter (the mechanism)

| Statement | s42 | s0 |
|---|---|---|
| Subsets at or above 50% ASR (of 62 hybrids) | 13 | 17 |
| All of them contain layer4 | yes | yes |
| All of them contain layer2 | yes | no ({1,4,5} = 59.94, {1,3,4,5} = 62.63) |
| Max ASR without layer4 | 7.46 ({0,2,5}) | 15.14 ({1,2,3,5}) |
| Max ASR without layer2 | 13.99 ({0,1,4,5}) | 62.63 ({1,3,4,5}) |
| Max ASR without layer3 (the largest share) | 84.83 ({0,1,2,4,5}) | 96.07 ({1,2,4,5}) |
| Subsets containing both layer2 and layer4: minimum ASR | 32.96 ({2,4}) | 50.52 ({0,2,4}) |
| Spearman rho, repair share covered vs ASR, 62 hybrids | 0.334 | 0.414 |

The replicated rule is: **layer4 is necessary; layer3 is dispensable; share is a weak predictor.** Layer2 is the usual partner but not necessary in s0. Do not write "both layer2 and layer4 are required" as a general claim; it holds for s42 only.

## 8. Cross-seed

Pearson r of ASR across all 64 subsets: **0.926**. The two repairs agree on whether a subset is above or below 50% ASR in **60 of 64** subsets. The four disagreements all contain layer4 without layer2: {1,3,4,5}, {1,4,5}, {2,4}, {1,3,4}.

In s0, three hybrids exceed the infected model's own ASR: {1,2,3,4} 95.82, {1,2,4,5} 96.07, {1,2,3,4,5} 96.49. None do in s42. One sentence, no more.

## 9. Hybrid clean accuracy, all k=1..5

s42: 74.76 to 93.15. s0: 79.87 to 93.52. No hybrid near random chance.

## 10. Old claim to new claim, for every number-bearing sentence

| Where | Old (legacy norm, s42 only) | New |
|---|---|---|
| Abstract, single shard | at most 8.94% | at most 16.4% (5.36 in s42, 16.40 in s0) |
| Abstract, CA of single-shard hybrids | 86.0 to 93.3 | 86.8 to 93.5 |
| Abstract, layer2+layer4 rule | every such subset >= 74.8% | replace with: every hybrid above 50% contains layer4; layer3 (48% of the repair) is dispensable |
| Abstract, headline | 3 shards, 92.89% at 87.38 | 4 shards ranked by share, 92.3 to 95.8% at CA within 2.3 of repaired |
| III-A baseline | 97.43 / 89.41; "re-trained" | 95.06 / 91.33, matches published; repaired 0.81/93.18 (s42) and 1.13/93.51 (s0) |
| III-B CA range | 84.58 to 93.26 | 74.76 to 93.15 (s42), 79.87 to 93.52 (s0) |
| Fig. 1 red bars | 1.02, n.t., 8.94, 0.50, n.t., 1.18 | 0.81, 0.91, 5.36, 0.40, 3.96, 1.09 (s42); add s0 as a second series or a second panel |
| Fig. 2 greedy curve | 0.90, 0.50, 4.57, 92.89, 97.11, 97.21, 97.43 | Section 3 above, both seeds |
| Fig. 3 three strategies | as drawn | Sections 3, 4, 5 above; "random" is now the exact mean |
| III-F "41 of 63", 11 / 30, >= 74.76, Spearman 0.65 | | all 63; Section 7 above; Spearman 0.33 / 0.41 |
| III-G determinism | as written | keep, and add the s0 replication: Section 8 above |
| Discussion "5.97 points below repaired, within 2.03 of infected" | {2,3,4} | k=4 greedy: 2.05 / 2.31 below repaired, within 0.2 of infected |
| Setup "CA even rises by 3.94 points" | | delete; gain over 91.33 is 1.85 (s42) and 2.18 (s0) |
