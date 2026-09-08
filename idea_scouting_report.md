# RIVF 2026 SS3 Idea Scouting Report

**Prepared:** 8 September 2026  
**Target:** RIVF 2026 Special Session SS3, *Recent Advances in 6G Communications: Technologies, Architectures, and Applications*  
**Constraint:** three strong final-year undergraduates, three weeks, six IEEE double-column pages

**Student starting point:** after choosing an idea, follow the [zero-to-one research tutorial](student_zero_to_one_tutorial.md) and complete the accompanying [research workbook](student_research_workbook.md). These explain how to turn the reading homework and candidate-specific experiments below into a reproducible study and a six-page manuscript.

## Decision

The best candidate is **Backdoor Repair Under Shard-Version Skew in Distributed Edge Inference**. It has the cleanest technical question, the lowest overlap with the accepted ATC papers, and a result that can be falsified within five days.

The two retained alternatives are **Precision-State Exposure in Channel-Adaptive Split Inference** and **Bounding AF_XDP Buffer Retention Under Bursty Telemetry**. Both fit SS3 and the existing research trajectory, but each must pass an early empirical gate before the team commits to a paper.

| Rank | Candidate | SS3 fit | Main research interest | Three-week outlook | Principal risk |
|---|---|---|---|---|---|
| 1 | Backdoor repair under shard-version skew | Strong | Distributed-system security + adversarial ML | Best balance | The effect may reduce to trivially undoing the repaired layer |
| 2 | Precision-state exposure in adaptive split inference | Very strong | Adversarial ML + distributed edge AI | Good pilot; uncertain result | Strong attacks may erase all precision-dependent differences |
| 3 | AF_XDP outstanding-frame isolation | Strong but systems-heavy | Distributed-system security + edge AI availability | Viable only with immediate Linux access | No implementation is present locally; closest 2026 controller work is near |

These are **conditional green lights**, not promises of acceptance. Each survived only after an Astra reviewer rejected a broader initial formulation and forced a narrower claim, threat model, and evaluation.

## Immediate deadline issue

The official pages conflict. The [main RIVF 2026 call](https://rivf2026.org/call-for-papers.html) says that **15 September 2026 is a hard deadline**, while the [SS3 page](https://rivf2026.org/special-session-ss3.html) lists **30 September 2026** as its tentative submission deadline. A three-week sprint from 8 September ends on 29 September and is viable only if the SS3 deadline controls. The first action should be written confirmation from the session chair or the general conference contact. Until that is confirmed, 15 September is the conservative deadline.

## What SS3 asks for

SS3 explicitly welcomes algorithm design, hardware prototypes, and system-level evaluations in:

- federated learning and distributed edge AI;
- generative AI and LLMs for network management;
- blockchain for decentralized 6G resource allocation;
- physical-layer security; and
- trust, privacy, and resilience in ultra-dense networks.

The session states that papers receive the same review standard as the main conference and at least two independent reviews. The [main call](https://rivf2026.org/call-for-papers.html) limits submissions to six A4 IEEE conference pages.

## RIVF's observable technical bar

The evidence does not justify inventing a numerical acceptance-rate claim. The useful signal is the type of work that appeared in the 2025 programme and proceedings.

The [RIVF 2025 proceedings contents](https://researchr.org/publication/rivf-2025) show that most regular papers occupy six pages. Relevant accepted examples include:

- *Rethinking Adversarial Robustness: The Role of Input Transformations*;
- *A Nonlinear Transformation-Based Defense Against Data Leakage in Federated Learning*;
- *Balancing Defence and Operational Stability: Resilience-Oriented Reinforcement Learning for Autonomous Critical Infrastructure Cyber Defence*;
- *Mind the Gap: On the Practical Utility of SHAP for Deep Learning-Based Intrusion Detection*;
- *Energy-Efficient Resource Allocation in O-RAN Using Soft Actor-Critic*; and
- *A Case Study With Concurrency and Data-Tensor Parallelism Scenarios in vLLM*.

This suggests a pragmatic IEEE conference bar. A paper need not contain a top-tier security proof or a large hardware testbed, but it should have:

1. one precise technical mismatch, not a broad “AI for 6G” motivation;
2. a reproducible implementation or controlled simulation tied to real measurements;
3. modern, correctly configured baselines;
4. adversarial, failure, or sensitivity experiments matching the claim; and
5. claims narrow enough to fit the evidence and six-page limit.

A generic classifier comparison, a synthetic 6G label attached to a conventional ML experiment, or a known primitive with a new name would sit below this bar.

## Fit with the existing paper portfolio

The accepted ATC papers establish two useful capabilities:

- [Compute-for-Bandwidth](/Users/hungdang/Papers/conferences_paper/ATC_tensor_cast/paper.tex) provides a channel-aware FP16/INT8/INT4 scheduling concept and a trace-driven fading scaffold for distributed edge inference.
- [Kernel Bypass for Deterministic Edge VR Telemetry](/Users/hungdang/Papers/conferences_paper/ATC_xdp_Telemetry/paper.tex) establishes AF_XDP normal-load tail latency, batching, CPU headroom, and co-located inference experiments.

The ICLIE work demonstrates compact streaming-state design, paired baselines, multi-seed experiments, and claim-to-evidence discipline. Its blockchain/fraud mechanisms do not directly implement any of the three candidates.

Two reuse limits matter:

- TensorCast's public proof of concept does not implement a valid round-trip INT4 codec; it truncates INT8 bytes. New precision experiments require genuine quantize, pack, unpack, dequantize, and inference code.
- No AF_XDP C implementation is present in the available workspace. Candidate 3 cannot assume that a working receiver harness is ready.

Any new paper must cite the accepted work, disclose infrastructure reuse, and generate entirely new attack, mechanism, and evaluation results. Reusing old text, old plots, or old headline measurements would create salami-slicing risk.

## Shared student reading method

Use the first two days for orientation and the closest required readings. Continue detailed reading and reproduction alongside implementation; the hands-on deliverables below extend into the pilot. Each student should produce a half-page note for every assigned item using the same five questions:

1. What exact system and attacker or failure model does the work assume?
2. What is genuinely new: observation, attack, mechanism, proof, implementation, or measurement?
3. Which figure or table carries the principal evidence?
4. Which baseline is the closest competitor, and is the comparison resource-matched?
5. Which assumption would most likely fail in our intended experiment?

The group should finish day 2 with a 30-minute teach-back per student, one shared terminology sheet, and a one-page “ours versus closest work” table. Reading without these deliverables is unlikely to help a three-week sprint.

---

## Candidate 1: Backdoor Repair Under Shard-Version Skew in Distributed Edge Inference

### One-sentence thesis

A backdoor repair that succeeds on the complete model may fail when a rolling 6G edge deployment serves one historically signed but stale model shard; the paper measures when partial rollback resurrects the backdoor and what availability cost is imposed by request-atomic model epochs.

### Concrete problem

Distributed edge inference partitions a model across workers and updates those workers under intermittent links. A model owner can discover a backdoor, repair the model, sign the new artifacts, and roll them out. Per-shard signature checking still permits a mix of individually valid historical components unless the deployment pins a complete model epoch. The security question is not whether old software can be replayed in general. It is whether reverting only one contiguous shard restores a repaired model's backdoor while most repaired parameters remain active and clean accuracy stays high.

### Threat model

- The adversary controls an artifact cache or update path and can supply a historically signed shard.
- The coordinator, loader, runtime, and persistent minimum-epoch state are trusted.
- The adversary cannot forge signatures or make a trusted runtime execute undeclared weights.
- A fully compromised worker that lies about its loaded weights is out of scope; defending against it requires attestation or verifiable computation.
- A stale honest worker is a corresponding non-malicious failure case.

This threat model is essential. A manifest alone does not defend against a compromised process that labels old computation as current.

### Exact research questions

1. After a complete-model backdoor repair, can one stale contiguous shard raise attack success substantially while retaining acceptable clean accuracy?
2. Which layers and repair-update distributions create this fragility?
3. How much unsafe service or refused service results from independent “latest version” selection compared with request-atomic epoch pinning during interrupted rollout?

### Permitted contributions

- A controlled measurement of backdoor-repair fragility under single-shard historical rollback.
- A layer/epoch heatmap relating backdoor reactivation to the fraction and location of reverted repair updates.
- A deployment experiment comparing independent per-shard validity checks with complete-manifest pinning and request-atomic version routing.
- An availability/security trade-off under delayed updates and reconnection.

Do not claim a new rollback-protection protocol. [TUF](https://theupdateframework.github.io/specification/draft/) and [Uptane](https://uptane.org/papers/uptane-standard.1.0.1.html) already establish signed snapshot, rollback, freeze, and mix-and-match defenses. Epoch pinning is the control that exposes the ML-specific effect.

### Minimum experiment

**Models and attacks.** Use [BackdoorBench](https://arxiv.org/abs/2407.19845), CIFAR-10, ResNet-18, two triggers, three seeds. Use ordinary clean fine-tuning and NAD as the two primary repair methods. Add PAM only for the strongest reproducible case because it explicitly targets post-purification reactivation.

**Partitions.** Freeze two- and four-stage contiguous partitions before observing attack outcomes. Enumerate each single-stage rollback. For four stages, the 16 old/new combinations are a useful diagnostic but not the main claim.

**Controls.** Measure the infected model, fully repaired model, whole-model rollback, single-shard rollback, and benign clean-lineage skew. Preserve batch-normalization buffers, preprocessing, quantizer state, and label maps consistently.

**Deployment.** Reproduce composition in one process, then use two to four actual worker processes. Compare independent valid-shard loading, exact manifest pinning, and request-atomic epoch routing during delayed update, restart, reconnection, and in-flight upgrade.

**Metrics.** Report backdoor attack success rate on non-target source examples, clean accuracy, class-level damage, fraction of repair update reverted, unsafe accepted requests, refusals, completion rate, p99 latency, rollout recovery time, and metadata bytes.

### Closest work that must be confronted

- [Min et al., NeurIPS 2024](https://arxiv.org/abs/2410.09838) shows that purified models can retain superficially suppressed backdoors that later reactivate.
- [DeferBad](https://arxiv.org/abs/2411.14449) deliberately makes backdoor unlearning fragile to later benign updates.
- [Subnet Replacement Attack](https://arxiv.org/abs/2107.07240) establishes deployment-stage backdoors through limited parameter replacement.
- [BadMerging](https://arxiv.org/abs/2408.07362) and [MergeBackdoor](https://www.usenix.org/conference/usenixsecurity25/presentation/wang-lijin) show that model composition can introduce or activate backdoors.
- [AIRS](https://arxiv.org/abs/2511.12668) narrows claims around per-shard hash checking and loader integrity.

The remaining gap is specifically **historically valid contiguous shard rollback after complete-model repair**, not generic model merging, generic backdoor reactivation, or signed-update security.

### Astra rebuttal and refinement

**Original verdict:** reject. The initial manifest protocol did not stop a compromised worker from claiming the current epoch while executing old weights, and the systems mechanism collided with TUF/Uptane.

**Refinement retained:** restrict the attacker to the artifact/update path with a trusted loader and runtime; make the paper a measurement of repair fragility; treat complete epoch pinning as an existing security control rather than a new cryptographic contribution.

### Day-5 kill gate

Continue only if all conditions hold:

- infected ASR is at least 80%;
- repaired ASR is at most 10%;
- one single-shard rollback raises ASR to at least 50%, or by at least 30 percentage points;
- clean accuracy falls by no more than two percentage points;
- the reverted shard does not contain the entire effective repair; and
- the result repeats on at least two seeds.

Kill the paper if the result merely swaps back the only repaired head/layer.

### Day-10 gate

Require two triggers, two repairs, correct handling of all model state, and a working multi-process rollout experiment. At least one second architecture or dataset confirmation should be underway.

### Three-student division

- **Student A:** BackdoorBench models, attack reproduction, repairs, and repair-update analysis.
- **Student B:** partition generator, shard substitution matrix, model-state correctness, and statistics.
- **Student C:** multi-process serving, manifests/epoch routing, interrupted-rollout tests, and latency measurement.

### Suggested paper keywords

`distributed edge inference`, `model version skew`, `backdoor repair`, `rollback attack`, `model sharding`, `secure model deployment`, `6G edge AI`

### Literature-search phrases

- `backdoor repair reactivation model shard rollback`
- `mix-and-match attack signed machine learning artifacts`
- `distributed inference rolling model update version consistency`
- `partial layer replacement backdoor attack`
- `model purification fragile backdoor unlearning`
- `Triton ensemble model version latest rolling update`

### Student reading homework

**Required for everyone**

1. [BackdoorBench paper](https://arxiv.org/abs/2407.19845) and [documentation](https://backdoorbench.github.io/docs/). Focus on the attack/defence pipeline, dataset construction, ASR denominator, configuration files, and reproducibility conventions. Deliverable: reproduce one published CIFAR-10 attack/defence pair and record the exact command, seed, checkpoint, clean accuracy, and ASR.
2. [TUF specification](https://theupdateframework.github.io/specification/draft/). Read the threat model and the roles of root, targets, snapshot, and timestamp metadata. Deliverable: state which metadata prevents rollback, freeze, and inconsistent component sets.
3. [Uptane standard](https://uptane.org/papers/uptane-standard.1.0.1.html). Read the attack taxonomy for rollback and mix-and-match of individually valid images. Deliverable: explain in five sentences why per-shard signatures do not imply whole-pipeline consistency.
4. [Superficial Safety of Backdoor Defense](https://arxiv.org/abs/2410.09838). Focus on how purified weights retain paths back to malicious behaviour. Deliverable: identify what would distinguish shard rollback from the paper's retuning/query reactivation.
5. [Subnet Replacement Attack](https://arxiv.org/abs/2107.07240). Focus on how limited parameter replacement creates deployment-stage backdoors. Deliverable: list the minimum result needed to show that historical-shard rollback is not merely a renamed subnetwork replacement attack.

**Role-specific reading**

- **Student A:** BackdoorBench defence recipes; [NAD](https://arxiv.org/abs/2101.05930); [DeferBad](https://arxiv.org/abs/2411.14449). Produce a table of what parameters/buffers each repair changes and how repair success is measured.
- **Student B:** [BadMerging](https://arxiv.org/abs/2408.07362) and [MergeBackdoor](https://www.usenix.org/conference/usenixsecurity25/presentation/wang-lijin). Produce the distinction among arbitrary model merging, malicious component construction, and replay of one historically valid contiguous shard.
- **Student C:** NVIDIA's [Triton ensemble documentation](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/ensemble_models.html) and [model-repository version policy](https://github.com/triton-inference-server/server/blob/main/docs/user_guide/model_repository.md). Produce a two-process toy pipeline that pins explicit component versions, then document what changes when `latest` is used.

**Group comprehension check.** Before experiments, the students must be able to explain why a signed artifact, a mutually consistent model epoch, and attested execution are three different guarantees.

### Six-page shape

Use one threat/deployment figure, one layer-version heatmap, one primary result table, and one rollout trade-off plot. The paper should spend roughly 1.25 pages on problem/threat/related work, 1 page on method and hypotheses, 0.75 page on implementation, 2.25 pages on results, and 0.75 page on limitations/conclusion.

---

## Candidate 2: Precision-State Exposure in Channel-Adaptive Split Inference

### One-sentence thesis

Channel-adaptive split inference exposes a small runtime state machine to an attacker; the paper tests whether observing or predicting its precision state enables materially more effective bounded-time adversarial inputs than attacking the stationary mixture of precision modes.

### Why the narrow framing matters

Quantized models can be more or less adversarially robust depending on model, quantizer, and attack. A Markov channel that merely selects among FP16, INT8, and INT4 models produces a weighted mixture of static results; that alone is not new. The contribution exists only if state observation or bounded submission timing provides an attack advantage under equal query and waiting budgets.

### Threat model

- The attacker controls inference inputs and knows the model, split point, quantizers, and scheduler.
- State knowledge has three separately evaluated levels: stationary distribution only, delayed/noisy client-visible observation, and perfect state as an upper bound.
- The attacker has fixed perturbation, query, and waiting budgets.
- The attacker does not control the wireless channel or model weights.
- Late, rejected, and misclassified results are different outcomes.

### Exact experiment

Use a frozen pretrained ResNet-18 and MobileNetV2. Implement genuine activation codecs at one or two fixed split points:

1. FP16 transfer;
2. calibrated INT8 activation quantization; and
3. actually packed and reconstructed INT4 activation quantization.

Implement three attacks:

- **Unaware:** optimize the exact weighted loss over all precision branches using their stationary probabilities.
- **Observed/predicted state:** optimize under the conditional precision distribution given the available observation.
- **Bounded timing:** prepare branch-specific adversarial examples and submit at the best predicted state within a fixed waiting window, charging all probing and waiting time.

Use exact forward quantization and BPDA/STE variants for gradients, multiple restarts, and losses appropriate to the task. Attack any detection or randomization branch jointly.

### Evaluation matrix

**Data.** CIFAR-10 pilot on two backbones; confirm the surviving configuration on a fixed ImageNet validation subset with a pretrained backbone. Use standard and publicly available robust checkpoints where practical.

**Channel.** Replay the accepted ATC scheduler structure as cited infrastructure, but use one independent throughput trace in addition to synthetic Markov fading. Vary observation delay and noise.

**Baselines.** Fixed precision; ordinary channel-adaptive scheduling; stationary-mixture attack; per-mode adaptive attack; resource-matched randomized precision; matched-cost precision escalation or prediction-disagreement screening as controls. Do not advertise a new MarginGuard defense.

**Metrics.** Evaluate only examples correctly classified by every compared clean mode. Report attack success, robust accuracy, payload, p99 deadline violation, waiting time, query count, late result, rejection, and “correct and on time” delivery.

### Closest work that limits the claim

- [On the Adversarial Robustness of Quantized Neural Networks](https://arxiv.org/abs/2105.00227) shows that quantization can improve or degrade robustness.
- [Random Precision Switch](https://arxiv.org/abs/2109.05223) already uses runtime precision switching as a robustness mechanism.
- [ARQ](https://arxiv.org/abs/2410.24214) treats mixed precision and certified robustness jointly.
- [QADT-R](https://arxiv.org/abs/2503.07058) attacks and defends across dynamic bit widths.
- [Zhang et al., Computer Networks 2025](https://doi.org/10.1016/j.comnet.2025.111755) studies adversarial attacks on latent representations in split computing.
- [Athalye et al.](https://proceedings.mlr.press/v80/athalye18a.html), [Tramèr et al.](https://arxiv.org/abs/2002.08347), and [AutoAttack](https://arxiv.org/abs/2003.01690) define the minimum standard for avoiding weak or obfuscated-gradient evaluations.

The defensible gap is not “quantization affects robustness.” It is the **measured value of exposed scheduler state and bounded timing in a channel-adaptive split system**.

### Astra rebuttal and refinement

**Original verdict:** reject. The original FadeTrigger framing assumed that poor channels imply weaker robustness, used standard EOT as if it were new, and proposed a local margin guard without a valid local logit source or secure high-precision fallback.

**Refinement retained:** remove the claimed new defense; make state information and bounded timing the independent variables; use a common-clean-correct cohort, strong adaptive attacks, real codecs, and explicit latency/query accounting.

### Day-5/7 kill gate

By day 5, genuine quantized inference and strong per-mode attacks must work. By day 7, continue only if state-aware bounded timing improves ASR by at least five percentage points on a fixed common-clean-correct cohort, on two model/split configurations, with at most one percentage point clean-accuracy difference between relevant modes. Kill if the gain requires instantaneous perfect CSI or disappears under stronger attacks.

### Day-10 gate

Require the effect to survive noisy/delayed observations, matched query and waiting budgets, randomized-precision baselines, and at least one robust checkpoint. Freeze the claims and experiment matrix at this point.

### Three-student division

- **Student A:** real activation codecs, split execution, and measured compute/communication timing.
- **Student B:** per-mode, mixture, state-aware, and bounded-timing attacks with adaptive-evaluation audit.
- **Student C:** channel replay, scheduler/state observation, matched-budget evaluation, statistics, and figures.

### Suggested paper keywords

`channel-adaptive edge AI`, `split inference`, `activation quantization`, `adversarial examples`, `adaptive attack`, `mixed-precision inference`, `6G edge intelligence`

### Literature-search phrases

- `adversarial robustness activation quantization bit width`
- `adaptive adversarial attack randomized precision model`
- `split computing latent representation adversarial attack`
- `channel adaptive edge inference quantization scheduler`
- `BPDA straight-through estimator quantized neural network attack`
- `state-aware timing attack adaptive inference system`

### Student reading homework

**Required for everyone**

1. The local accepted [Compute-for-Bandwidth paper](/Users/hungdang/Papers/conferences_paper/ATC_tensor_cast/paper.tex), especially its system, threat-model, evaluation, and scheduler sections. Deliverable: a table separating reusable infrastructure from claims, measurements, text, and figures that cannot be reused.
2. [On the Adversarial Robustness of Quantized Neural Networks](https://arxiv.org/abs/2105.00227). Focus on why lower precision can either improve or reduce measured robustness. Deliverable: write three confounders that could create a false precision effect.
3. [Random Precision Switch](https://arxiv.org/abs/2109.05223) and [QADT-R](https://arxiv.org/abs/2503.07058). Focus on attacks that know or do not know the active bit width. Deliverable: define the information available to the unaware, observed-state, and oracle attackers.
4. [Obfuscated Gradients](https://proceedings.mlr.press/v80/athalye18a.html), [Adaptive Attacks](https://arxiv.org/abs/2002.08347), and [AutoAttack](https://arxiv.org/abs/2003.01690). Deliverable: an attack-audit checklist covering exact forward passes, BPDA/STE, restarts, loss functions, transfer/query checks, and joint attacks on every defence branch.
5. Current [PyTorch quantization guidance](https://docs.pytorch.org/docs/stable/quantization.html). Note that PyTorch is moving quantization development toward TorchAO. Deliverable: specify scale granularity, zero point, clipping, rounding, packing, dequantization, and calibration data for each planned codec.

**Role-specific reading**

- **Student A:** [PyTorch quantization API reference](https://docs.pytorch.org/docs/main/quantization-support.html) and the local tensor codec/evaluation code. Produce a round-trip property test showing bounded error for FP16, INT8, and packed INT4 tensors; byte truncation is not an acceptable INT4 implementation.
- **Student B:** [ARQ](https://arxiv.org/abs/2410.24214) and the [split-latent attack paper](https://doi.org/10.1016/j.comnet.2025.111755). Produce a threat-model comparison and an adaptive attack plan that cannot be dismissed as gradient masking.
- **Student C:** [Channel-Adaptive Edge AI](https://arxiv.org/abs/2603.03146) plus the local channel simulator. Produce a state-transition diagram specifying what the client can observe, observation delay, scheduler memory, waiting budget, and when an input is committed.

**Group comprehension check.** Before the pilot, the students must be able to prove that an input-independent scheduler with no temporal attack choice yields only a precision-weighted mixture of static-model attack outcomes. This explains why state information and bounded timing—not the Markov trace itself—must carry the contribution.

### Six-page shape

The paper needs two central figures: a state/attack timeline and a precision-state robustness/deadline frontier. Use one compact table for model, split, codec, threat, and budget settings. Do not spend space proposing and training a new defense.

---

## Candidate 3: Bounding AF_XDP Buffer Retention Under Bursty Telemetry for Co-Located Edge Inference

### One-sentence thesis

AF_XDP queue occupancy is not the same as outstanding UMEM work, so a userspace feedback controller can react too late to short adversarial bursts or held frames; immediate per-class outstanding-frame credits may preserve protected telemetry and an inference SLO where occupancy feedback and static policing do not.

### Technical distinction

The paper must distinguish three resources:

1. RX descriptors waiting for userspace;
2. UMEM frames that remain unavailable after dequeue while authentication/application processing retains them; and
3. CPU spent in NAPI/XDP and userspace processing.

The contribution is not “XDP drops DDoS traffic” or “a feedback controller changes a token bucket.” Both are established. The publishable result would be a demonstrated AF_XDP-specific blind interval and a correct outstanding-frame accounting mechanism.

### Threat and trust model

- One receive queue carries two traffic classes assigned by a trusted ingress/VLAN/slice mapping.
- The attacker controls best-effort traffic timing and rate but cannot forge the protected class.
- A compromised sender inside the protected class is out of scope.
- The mechanism protects admitted host work and co-located inference; it does not protect upstream wireless capacity or guarantee service under unlimited line-rate attack.

### Exact mechanism

Use separate AF_XDP RX service for the two classes while explicitly managing shared-UMEM ownership.

- XDP maintains per-class admission-attempt counters.
- Userspace returns reclamation acknowledgements only after processing completes and the frame is safely returned to the correct FILL ownership path.
- Before redirect, an immediate outstanding-frame cap prevents best-effort traffic from consuming a non-borrowable protected reserve.
- Failed redirects are handled conservatively with a defined quiesce-and-reconcile procedure; a timeout is not assumed to prove safe credit return.
- A slow controller adjusts only the best-effort allowance from measured completion rate and inference slack.
- RX depth, FILL availability, held frames, pending application work, and CPU are measured separately.

### Required baselines

1. unprotected AF_XDP;
2. tuned static per-class XDP policing;
3. static policing plus protected RX/service reservation;
4. occupancy- or CPU-feedback adaptive policing; and
5. immediate outstanding-frame guard plus slow adaptation.

Ordinary UDP and cgroup CPU isolation are contextual comparisons. IRQ/NAPI affinity and CPU allocation must be documented.

### Required attacks and experiments

Vary burst duration around the measured feedback delay. Independently vary frame-retention time using normal processing, delayed authentication, receiver descheduling, and temporary application stalls. Test steady flood, microburst, low-rate on/off occupancy attack, and an attacker adapted to the controller period.

Report protected packets delivered before deadline divided by protected packets offered, drops, survivor latency, inference deadline misses and throughput, outstanding frames, RX depth, FILL starvation, reconciliation events, and total host receive-path/user-space CPU. Compare useful-telemetry-versus-inference-SLO frontiers, not just equal offered load.

Namespaces/veth are acceptable for development. The principal evidence should use two Linux VMs/hosts or a physical NIC, with generic/native XDP and COPY/ZEROCOPY named explicitly.

### Closest work and overlap limits

- [Closed-Loop CPU-Aware Traffic Control for SDN-Enabled 5G/6G Networks](https://www.mdpi.com/2624-6511/9/6/91) already combines eBPF telemetry, userspace feedback, XDP map updates, per-slice CPU protection, and 5G/6G framing.
- [Performance Implications at the Intersection of AF_XDP and Programmable NICs](https://cs.nyu.edu/~apanda/assets/papers/ebpf25.pdf) studies AF_XDP ring contention, batching, NAPI placement, and CPU starvation.
- [FLASH](https://www.cse.iitb.ac.in/~mythili/research/papers/2025-flash.pdf) addresses AF_XDP resource management and isolated UMEM configurations.
- [eBPF-Based Real-Time DDoS Mitigation for IoT Edge Devices](https://arxiv.org/abs/2508.00851) establishes early XDP rate-based flood blocking.
- The [Linux AF_XDP documentation](https://docs.kernel.org/networking/af_xdp.html) defines shared UMEM, RX/FILL/COMPLETION ownership, starvation, and wakeup behavior.

The accepted ATC XDP paper already evaluates Poisson bursts, batching, bounded polling, authentication cost, and co-located inference. The RIVF paper must contribute new adversarial resource accounting, new admission logic, and wholly new experiments. Merely relabeling traffic as malicious is not sufficient.

### Astra rebuttal and refinement

**Original verdict:** reject. A queue-pressure feedback controller collides with 2026 adaptive XDP policing and cannot stop a burst shorter than its control delay. RX occupancy alone misses frames retained after dequeue.

**Refinement retained:** add immediate outstanding-frame credits and a non-borrowable reserve; separate ring, frame, and CPU pressure; use slow adaptation only outside the blind interval; directly compare against static policing plus reservation.

### Day-5 kill gate

Stop unless the team has a reproducible AF_XDP receiver, traffic generator, and inference harness on suitable Linux machines. Also stop if tuned static policing resolves the attack at matched useful throughput, or if no repeatable distinction appears between RX occupancy and held-frame pressure.

### Day-10 gate

Continue only if the complete guard has no unexplained frame/counter drift under deliberate stalls and repeated bursts, and it achieves either:

- at least 20% higher useful telemetry throughput at the same protected-telemetry and inference SLO; or
- materially fewer SLO violations at matched useful throughput,

relative to tuned static policing plus reservation, across more than one attack pattern and a second configuration.

### Three-student division

- **Student A:** AF_XDP/XDP data path, UMEM ownership accounting, redirect-failure reconciliation.
- **Student B:** traffic generator, adversarial burst timing, namespace/VM/NIC automation, and CPU affinity.
- **Student C:** co-located inference harness, control loop, measurements, statistical analysis, and figures.

### Suggested paper keywords

`AF_XDP`, `eBPF/XDP`, `UMEM`, `buffer retention`, `resource isolation`, `adversarial microbursts`, `edge AI availability`, `6G telemetry`

### Literature-search phrases

- `AF_XDP FILL ring starvation UMEM frame ownership`
- `AF_XDP shared UMEM resource isolation`
- `XDP adaptive rate limiting feedback control microburst`
- `AF_XDP NAPI CPU contention userspace polling`
- `kernel bypass denial of service co-located inference`
- `eBPF 5G 6G per-slice CPU protection`

### Student reading homework

**Required for everyone**

1. The kernel's [AF_XDP documentation](https://docs.kernel.org/networking/af_xdp.html). Focus on UMEM, FILL and COMPLETION rings, RX/TX ownership, shared-UMEM restrictions, `need_wakeup`, COPY/ZEROCOPY, and redirect failures. Deliverable: draw the complete frame-ownership state machine and mark exactly when a credit can safely be returned.
2. The [XDP hands-on tutorial](https://github.com/xdp-project/xdp-tutorial). Complete the basic lessons and the redirect/map material relevant to the experiment. Deliverable: load an XDP program on a veth pair, update a map from userspace, and collect per-action counters.
3. [Performance Implications at the Intersection of AF_XDP and Programmable NICs](https://cs.nyu.edu/~apanda/assets/papers/ebpf25.pdf). Focus on queue/ring contention, batching, NAPI placement, and CPU starvation. Deliverable: identify which observed phenomena are already known and cannot be presented as new.
4. [Closed-Loop CPU-Aware Traffic Control for SDN-Enabled 5G/6G Networks](https://www.mdpi.com/2624-6511/9/6/91). Focus on its feedback signal, controller interval, XDP-map actuation, slice model, and evaluation. Deliverable: one paragraph stating the exact additional failure that outstanding-frame accounting must expose.
5. The local accepted [AF_XDP telemetry paper](/Users/hungdang/Papers/conferences_paper/ATC_xdp_Telemetry/paper.tex), especially evaluation methodology and results. Deliverable: an overlap table identifying prior workloads, packet distributions, batching, authentication, CPU measurements, and inference experiments.

**Role-specific reading**

- **Student A:** the kernel AF_XDP document again at implementation depth, plus libbpf examples referenced by the XDP tutorial. Produce a minimal receiver with explicit assertions for frame conservation across RX, application-held, COMPLETION, and FILL states.
- **Student B:** [FLASH](https://www.cse.iitb.ac.in/~mythili/research/papers/2025-flash.pdf) and [eBPF-Based Real-Time DDoS Mitigation for IoT Edge Devices](https://arxiv.org/abs/2508.00851). Produce a baseline matrix separating UMEM isolation, static policing, adaptive policing, and the proposed immediate credit guard.
- **Student C:** review Linux CPU affinity, IRQ/NAPI accounting, cgroups, and the inference harness used by the accepted ATC paper. Produce an accounting plan that captures XDP/NAPI CPU outside the inference process's cgroup rather than reporting only process CPU.

**Group comprehension check.** Before implementation, the students must be able to construct an example with low RX-ring occupancy but FILL starvation caused by application-held frames, and a second example where early XDP drops protect UMEM but still consume host receive-path CPU.

### Six-page shape

Use one ownership/accounting diagram, one blind-interval timeline, and two result plots. Limit formal claims to frame conservation and bounded admitted outstanding work. Avoid broad DDoS, 6G-core, or guaranteed-delivery claims.

---

## Ideas explicitly dropped after Astra rebuttal

These should not be revived without a materially new insight.

### Coordinated jamming plus poisoning in wireless FL

The initial “QuorumShift” idea directly collided with [Barkatsa et al., IEEE OJCOMS 2025](https://doi.org/10.1109/OJCOMS.2025.3558672), which already studies coordinated suppression of legitimate uploads and poisoned contributions. [Allouah et al., ICML 2024](https://proceedings.mlr.press/v235/allouah24a.html) and [Otsuka et al.](https://arxiv.org/abs/2509.02970) also cover Byzantine amplification under client subsampling/partial participation. This is not a safe novelty position for a three-week paper.

### Quantization-aware Freivalds checks for outsourced inference

The initial “SpotFreivalds” idea directly overlapped [Slalom](https://arxiv.org/abs/1806.03287), which already quantizes and precomputes fixed-weight Freivalds checks. Recent work such as [VeriAttn](https://arxiv.org/abs/2606.16352) further occupies tolerant checks for LLM operators. Numerical tolerance also creates an adversarial acceptance region, so a calibrated threshold does not supply the claimed integrity guarantee.

### New low-latency sealed auction for 6G edge resources

The replacement blockchain idea collided with [Censorship-Resistant Sealed-Bid Auctions on Blockchains](https://arxiv.org/abs/2606.14939), [Scalable Off-Chain Auctions at NDSS 2026](https://www.ndss-symposium.org/wp-content/uploads/2026-s410-paper.pdf), and prior [sealed-bid allocation of geo-distributed edge resources](https://research.ibm.com/publications/decentralized-allocation-of-geo-distributed-edge-resources-using-smart-contracts). A measurement-only fairness/deadline study remains possible, but it is less aligned with the available capabilities than the three selected candidates.

## Shared three-week operating plan

The team should run **one candidate**, not all three.

### Days 1–2: reproduction before invention

- Freeze the threat model, primary hypothesis, datasets, baselines, and success threshold.
- Reproduce the nearest public baseline and the relevant local setup.
- Create one command that runs a tiny end-to-end experiment and records configuration, seed, commit, environment, and raw output.

### Days 3–5: falsification pilot

- Run the day-5 kill gate exactly as written.
- Use paired seeds and preserve failures.
- If the effect is absent, stop. Do not weaken attacks, remove baselines, or change denominators to save the idea.

### Days 6–10: mechanism and decisive comparison

- Implement only the minimum mechanism needed to test the hypothesis.
- Complete the closest-baseline comparison under matched resources.
- Freeze claims, experiment matrix, and figure plan at day 10.

### Days 11–15: evidence

- Run multi-seed main experiments, one confirmation configuration, ablations, and explicit failure cases.
- Generate plots from stored raw data.
- Maintain a claim–evidence table with the exact source file and script for every number.

### Days 16–18: six-page manuscript

- Write the problem, threat model, and contribution boundaries first.
- Keep challenge–solution–evaluation order consistent.
- Use two or three figures with one argumentative job each and at most two compact tables.

### Days 19–21: adversarial audit

- Re-run headline results from a clean environment.
- Audit adaptive attacks, denominators, uncertainty, and resource matching.
- Check overlap with the ATC papers sentence by sentence and figure by figure.
- Build the exact IEEE A4 six-page PDF and inspect it visually.

## Final recommendation

Start with **Candidate 1** immediately after confirming the SS3 deadline. It offers the cleanest independent story:

> A complete-model backdoor repair is not necessarily a safe deployed repair when edge workers update non-atomically; one historically valid shard may restore the attack.

The first five days buy the answer cheaply. If the single-shard effect fails the stated gate, switch to **Candidate 2** only if the genuine precision codecs and pretrained checkpoints are already ready. Select **Candidate 3** only if a working AF_XDP environment is available on day 1; otherwise, setup risk will consume the paper window.
