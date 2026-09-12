# Project Agreement

## Section 1: Project Metadata

- **Project title:** Backdoor Repair Under Shard-Version Skew in Distributed Edge Inference
- **Date / revision:** 08/09/2026 — Rev 1.0
- **Team members and supervisor:** Dương Ngọc Linh Đan, Hồ Du Tuấn Đạt, Nguyễn Minh Chính; Supervisor: Dr. Đặng Khánh Hưng
- **Chosen candidate:** Candidate 1 — Backdoor Repair Under Shard-Version Skew in Distributed Edge Inference
- **Submission track, verified deadline, and source:** RIVF 2026, Special Session SS3 (*Recent Advances in 6G Communications*). Deadline pending written confirmation from the session chair — the SS3 page lists 30/09/2026 as tentative, while the main call for papers lists 15/09/2026 as a hard deadline. Working assumption: 29/09/2026, to be revised upon confirmation.

## Section 2: Core Research Problem

- **Concrete deployment example:** An edge inference service detects a backdoor, performs a complete model repair, and re-signs all resulting artifacts. During an interrupted rollout — where some workers have received the patched shards and others remain stale due to intermittent connectivity — a compromised artifact cache supplies one shard that was validly signed under a prior, pre-repair version. Because workers verify each shard's signature independently rather than the consistency of the full model epoch, the system may unknowingly serve a hybrid model composed of both repaired and stale components.

- **Research question:** After a backdoor has been fully repaired across a model, does rolling back a single contiguous shard to its historically valid (pre-repair) state significantly restore the attack success rate relative to the fully repaired model — while clean accuracy remains largely preserved — compared against whole-model rollback and a benign clean-lineage skew control?

- **Hypothesis:** A single historically valid shard, when reintroduced into an otherwise repaired model, can restore a substantial fraction of the original backdoor's attack success rate — particularly when that shard contains layers carrying most of the repair's effective weight updates — while the remainder of the model stays repaired and clean accuracy remains largely unaffected.

- **Proposed contribution (still unverified):** An unverified, quantitative measurement of backdoor-repair fragility under single-shard historical rollback, accompanied by a layer/epoch heatmap localizing fragility, and a multi-process deployment experiment comparing independent per-shard validity checking against complete-manifest epoch pinning in terms of both security and availability.

- **Closest prior work and exact remaining difference:**
  - Min et al. (NeurIPS 2024) — shows purified backdoors can reactivate via retuning or querying; **difference:** this work tests reactivation via rollback of a historically valid shard, not via retuning.
  - DeferBad — deliberately engineers unlearning to be fragile to subsequent benign updates; **difference:** this work examines fragility to rollback toward a prior historical state, not forward benign updates.
  - Subnet Replacement Attack — allows the attacker to freely select replacement parameters; **difference:** this work restricts the attacker to shards that were historically valid and signed, not arbitrary parameter substitution.
  - BadMerging / MergeBackdoor — address deliberate merging across distinct model sources; **difference:** this work concerns partial rollback within a single, known model lineage, not merging across sources.
  - AIRS — narrows to per-shard hash/signature and loader integrity checks; **difference:** AIRS does not address a shard that is valid in hash/signature but belongs to a stale epoch — precisely the gap addressed here.
  - TUF / Uptane — already establish rollback and mix-and-match detection at the snapshot-metadata level; **difference:** this work does not propose a new protocol; epoch pinning is used as an existing control, and the contribution is measuring the ML-specific consequence of its absence.

## Section 3: Threat Model & Trust Assumptions

- **Attacker objective:** Cause the system to serve a hybrid model composed of repaired and historically stale shards, restoring backdoor behavior without detection through per-shard signature checks.

- **Attacker knowledge:** Model architecture, shard partition boundaries, and possession of at least one shard validly signed under a pre-repair version.

- **Attacker control:** The artifact cache or update path — capable of supplying a historically valid shard to a worker during an interrupted rollout.

- **Attacker budget (queries / time / bytes / compromised components):** Compromised components limited to the artifact cache/update path (excluding workers, coordinator, loader, and runtime). No query or byte budget applies, as this is not a query-based attack; a single well-timed shard substitution during rollout interruption suffices.

- **Trusted components:** Coordinator, loader, runtime, and persistently stored minimum-epoch state. The attacker cannot forge signatures or cause the runtime to execute undeclared weights.

- **Out-of-scope capabilities:**
  - A fully compromised worker that misrepresents its currently loaded weights — this requires attestation or verifiable computation and falls outside this project's scope.
  - Forgery of signatures or compromise of the trusted loader/runtime.

## Section 4: Evaluation & Metrics

- **Primary outcome and denominator:** Attack Success Rate (ASR) = number of eligible triggered examples classified as the attacker's target label / total number of eligible triggered examples evaluated (excluding examples already belonging to the target class).

- **Benign utility and resource-cost metrics:** Clean accuracy, class-level damage, fraction of repair update reverted, unsafe accepted requests, refusal rate, completion rate, p99 latency, rollout recovery time, metadata overhead (bytes).

- **Strongest necessary baseline:** Comparison against (a) the fully repaired model without rollback, (b) whole-model rollback, and (c) a benign clean-lineage skew control (two distinct clean checkpoints, no backdoor present) — required to isolate the backdoor-specific effect from any generic consequence of version mismatch.

- **Smallest experiment:** For a four-stage model f(x) = f4(f3(f2(f1(x)))), begin with a fully repaired model of known state, substitute exactly one stage with its historical state, hold inputs, labels, evaluation mode, and remaining stages fixed, and measure ASR and clean accuracy.

- **What result would make us stop:** If post-rollback ASR fails to meet the predefined gate (an increase of at least 50%, or at least 30 percentage points, relative to the fully repaired model) across at least two seeds, or if the rolled-back shard is found to contain the entirety of the repair's effective weight update (i.e., the result merely undoes the repair) — the project is halted.

- **What observation would indicate a bug:** Baseline ASR/clean accuracy (infected and fully repaired models) deviating from BackdoorBench's published values beyond a reasonable tolerance; or inconsistent handling of batch-normalization buffers, quantizer state, or label maps during shard substitution — verified by comparing the output of a "shard-substituted, state-preserved" configuration against an independently run full model.

## Section 5: Logistics & Execution

- **Available hardware / datasets / checkpoints:** [To be completed — specify available GPU type and count, access arrangement, dataset (CIFAR-10 via BackdoorBench), checkpoint availability, and storage capacity]
%%Hung: Confirmed compute plan — you do NOT need paid cloud GPU.
%%Hung:  - Primary machine: my M2 MacBook (PyTorch MPS backend, device="mps"). CIFAR-10 models (~11M params) are tiny; unified memory is never the bottleneck.
%%Hung:  - Optional overflow: free T4 via Kaggle (30 GPU-hrs/week, persistent storage — prefer over Colab-free) or Colab. Use only to parallelize seeds or a slow repair run; not required.
%%Hung:  - Dataset: CIFAR-10 via BackdoorBench.
%%Hung: CHECKPOINT REUSE (verified 12/09/2026): BackdoorBench publishes the backdoored (attacked) models + poisoned train/test data on SharePoint (cuhko365.sharepoint.com) and Google Drive, and clean_model files too. This ELIMINATES attack training — the one expensive step. Source: github.com/SCLBD/BackdoorBench, paper arXiv:2401.15002.
%%Hung:  - DOWNLOAD: the infected PreAct-ResNet18 / CIFAR-10 checkpoint (BadNets, and Blended if used) + the matching clean model.
%%Hung:  - PRODUCE LOCALLY: the repaired checkpoint, by running a defense (fine-pruning / i-BAU / ANP) on the downloaded infected model — cheap fine-tuning (~0.5 h), fits on the M2.
%%Hung:  - CAVEAT: repaired/defended weights are NOT published — only attacked + clean. Also the README does not enumerate exact files, so Chính must confirm the specific infected checkpoint is actually present on the Drive before we rely on it (fallback: train that one checkpoint on the free T4).
%%Hung:  - PROVENANCE: for every reused checkpoint record source URL, exact filename, and SHA256 in Run Record (Form E). This matters — our whole claim is about epoch/version lineage, and it lets a reviewer reproduce from identical base weights.
%%Hung: Storage: checkpoints are tens of MB; commit them to this repo or attach as a GitHub release so every machine pulls the same bytes.

- **Missing prerequisites, owner, and resolution date:** [To be completed — e.g., BackdoorBench environment setup pending, owner and target date; SS3 deadline confirmation pending, owner and target date]
%%Hung: DEADLINE IS FIXED: 29/09/2026 — 17 days from today (12/09/2026). Plan every gate against this date. The 15/09 line in Section 1 is the main-track CFP and does NOT bind SS3; treat 29/09 as operative. Đạt: still get written confirmation from the SS3 chair, but do not wait on it to start — resolution by Day 2 (14/09).
%%Hung: Prerequisites and owners:
%%Hung:  - BackdoorBench environment runs on CUDA out of the box; on the M2 set PYTORCH_ENABLE_MPS_FALLBACK=1 and fix a few hard-coded device="cuda" strings. Owner: Chính. By Day 2 (14/09).
%%Hung:  - Confirm the published infected checkpoint downloads and loads. Owner: Chính. By Day 2 (14/09).
%%Hung:  - Pick ONE repair/defense method and freeze it. Owner: Chính. By Day 3 (15/09).
%%Hung:  - Do not sweep architectures/triggers. Fix PreAct-ResNet18 + at most 2 triggers (BadNets, Blended), 2 seeds for the gate. 17 days does not allow a matrix.

- **Estimated pilot compute cost:** [To be completed following a timed sample run, scaled by the planned combination of architectures, triggers, repair methods, partitions, and seeds, against actual available GPU resources]
%%Hung: With attack training removed by checkpoint reuse, the only GPU work is repair fine-tuning (~0.5 h/checkpoint). Everything downstream is cheap:
%%Hung:  - Shard-substitution matrix -> ASR / clean-accuracy is INFERENCE-ONLY: minutes, runs on CPU/M2.
%%Hung:  - Multi-process serving + latency/rollout-recovery is CPU orchestration: no GPU at all.
%%Hung: Estimated total: a few GPU-hours across the whole project. Cost = $0 (M2 alone suffices; free T4 optional). Still do one timed sample run (Đan) to confirm before committing seeds.
%%Hung: MEASUREMENT RULE: run every latency/timing number on ONE fixed, quiet machine (the M2) — never on a shared cloud VM. Cloud numbers are throttled and non-comparable; the T4 is for producing checkpoints only.

- **Student responsibilities and second readers:**
  - Nguyễn Minh Chính: BackdoorBench setup, attack/repair reproduction, repair-update distribution analysis. Second reader: Hồ Du Tuấn Đạt or Dương Ngọc Linh Đan.
  - Dương Ngọc Linh Đan: Partition generator, shard substitution matrix, model-state correctness verification, statistical analysis. Second reader: Nguyễn Minh Chính or Hồ Du Tuấn Đạt.
  - Hồ Du Tuấn Đạt: Multi-process serving implementation, manifest/epoch routing, interrupted-rollout experiments, latency measurement. Second reader: Nguyễn Minh Chính or Dương Ngọc Linh Đan.
%%Hung: Roles are good. Two additions: (1) Chính owns checkpoint provenance (source, filename, SHA256 in Form E) since he handles downloads. (2) Đạt runs ALL latency numbers on the single fixed M2 per the measurement rule above. Every result still needs its second reader before it enters the paper.

- **Day-5 decision date:** [To be completed — calculated from the actual project start date, not from the illustrative schedule's Day 0]
%%Hung: Start = Day 0 = today, Fri 12/09/2026. Deadline 29/09/2026. Compressed 17-day calendar (checkpoint reuse buys us this):
%%Hung:  - Day 0-2 (12-14/09): env up, download + load infected/clean checkpoints, reproduce baseline ASR/clean-acc against BackdoorBench numbers.
%%Hung:  - DAY-5 GATE = Wed 17/09: run the smallest single-shard substitution. STOP unless post-rollback ASR rises >=50% or >=30pp over the repaired model across 2 seeds AND the rolled-back shard is not simply the whole repair update.
%%Hung:  - DAY-10 GATE = Mon 22/09: full substitution matrix + layer/epoch fragility heatmap + serving comparison (per-shard check vs epoch-manifest pinning) showing security AND availability.
%%Hung:  - 23-27/09: write the six pages (results -> method -> intro -> related -> abstract last).
%%Hung:  - 28-29/09: adversarial self-audit, then submit. Leave a full day of slack before the deadline.
%%Hung: If the Day-5 gate fails, we pivot or drop — do not burn the remaining days chasing a null effect.
