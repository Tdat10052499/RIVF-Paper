# From an Idea to Your First Research Paper

A practical tutorial for a three-student team working toward a six-page RIVF paper

## Before you begin

You do not need to understand an entire research field before starting your first experiment. You need to understand one question well enough to test it carefully. Your understanding will grow as you read, build, encounter failures, and explain what happened to one another.

It is quite normal to read a paper and understand only half of it. It is also normal for your first reproduction to disagree with the published result. Neither means you are unsuited to research. They mean you have reached something that needs investigation. Keep a record of what you expected, what you observed, and what you will check next.

This guide begins after your team chooses one of the three ideas in the [scouting report](idea_scouting_report.md). It explains a common workflow that works for an attack study, a systems measurement paper, or a small mechanism with an experimental evaluation. The accompanying [research workbook](student_research_workbook.md) provides forms you can copy into your project.

Our intended outcome is a paper whose main finding another researcher can understand, challenge, and reproduce. A three-week schedule makes careful scope particularly valuable. The shortlist contains research hypotheses; none of its expected effects has been established by our own experiments yet.

All numerical examples in this tutorial are **invented teaching examples**, not results from the proposed papers. Thresholds in the scouting report are project-selection criteria, not predicted measurements.

## 1. Understand what you are trying to produce

A research paper answers a question using evidence and explains how that answer changes what we know. Your implementation makes the experiment possible. The paper explains why the experiment matters, whether the comparison is fair, and what the result supports.

Consider this sequence:

> An edge deployment updates different model shards at different times. We suspect that a previously repaired backdoor can return during this transition. We construct the smallest valid experiment, compare complete and partial updates, and measure the attack outcome. Then we investigate which parts of the repair were undone and how deployment policies affect exposure.

There are several distinct statements here. “We suspect” introduces a **hypothesis**. The question being tested is a **research question**. The observed outcome is a **result**. A result becomes a **contribution** when its significance and difference from existing work are established.

Here are terms you will use every day:

| Term | Plain meaning | Example |
|---|---|---|
| Baseline | A comparison system or method | The same pipeline with explicit model-version pinning |
| Variable | Something that can change | Which shard serves an old checkpoint |
| Control | A condition used to rule out another explanation | Skew between two clean checkpoints |
| Ablation | A version with a component removed or replaced | Buffer admission without the immediate credit guard |
| Threat model | What the attacker can know, control, and afford | Control over an artifact cache but no ability to alter the trusted loader |
| Metric | A precisely defined measurement | Target-label predictions divided by eligible triggered examples |
| Artifact | Materials needed to inspect or repeat the research | Code, configurations, model provenance, logs, and figure scripts |
| Limitation | A boundary on the interpretation of a finding | A result measured on one architecture and two repair methods |

**Your first task:** explain the chosen idea to a teammate in two minutes. Use a concrete request, packet, model, or update as your example. If you cannot yet explain the failure, draw the sequence and identify the point where you become uncertain. That point is your next reading task.

## 2. Make a one-page project agreement

Before dividing the coding, agree on what the team is investigating. Otherwise, three capable students can build three incompatible interpretations of the same idea.

Complete the project-agreement form in the workbook. It should name the question, hypothesis, attacker, trusted components, main comparison, first experiment, available equipment, and stopping condition. Include one sentence describing the contribution you hope to make, marked **proposed**.

A useful research-question pattern is:

> Under [specific setting], does [controlled change] affect [measured outcome], compared with [baseline], while holding [important conditions] fixed?

For the three candidates, this becomes:

| Candidate | First research question | First controlled change | Essential comparison |
|---|---|---|---|
| Shard-version skew | Does one historical shard restore a backdoor after repair, while other repaired shards remain active? | Substitute one complete shard state | Fully repaired model and whole-model rollback |
| Precision-state exposure | Does observing precision before choosing an attack increase its success within a fixed time and query budget? | Information available to the attacker | Attack optimized for the same mixture without state information |
| AF_XDP buffer retention | Can held frames exhaust available buffers while RX occupancy stays low, and can immediate admission limits help? | Frame retention and burst duration | Tuned policing with service reservation and delayed feedback |

Choose one primary outcome. You will also need measures of cost and benign utility. For example, an attack success rate is incomplete without clean accuracy, and an inference latency is incomplete without the number of requests dropped or refused.

Estimate what you can actually run. List GPU access, Linux hosts, storage, datasets, existing checkpoints, and any external cost. Obtain the required compute through your supervisor before designing a project around it. Candidate 3 particularly depends on a working Linux networking environment.

**Checkpoint:** all three students should agree on the same question and be able to name an outcome that would make the hypothesis uninteresting or false. Ask your supervisor to resolve major scope or threat-model disagreements early.

## 3. Read with a question in mind

Use the candidate-specific packet in the scouting report. Spend the first two days orienting yourselves and reading the closest work; continue focused reading alongside implementation. The two-day target does not mean completing every proof, reproduction, and programming exercise in the packet within 48 hours.

Start with one background resource, one closest research paper, and one implementation guide. Read the abstract, introduction, main diagram, experiment settings, and conclusion first. Write a short account in your own words. Then return to the method or proof sections needed for your experiment.

For each close paper, record five things: its precise claim, assumptions, mechanism, decisive evidence, and difference from your proposed question. Include the exact section, table, or figure that supports your interpretation. An abstract helps you find a paper; the body is needed to establish what it actually tested.

Build a small comparison table, initially containing three to five papers. Useful columns are attacker control, trusted components, what changes in the experiment, main result, available code, and the remaining difference. A table with these columns often exposes that two papers with different titles study the same problem.

For example, knowing that software-update systems already prevent inconsistent combinations of signed components changes the shard-skew project. The research opportunity becomes the behavior of repaired neural networks during such combinations. The version policy becomes a standard comparison mechanism.

If you find a very similar paper, record it immediately. This is useful progress. Reconsider the gap before spending a week implementing something already answered. Publication year and venue alone do not determine whether the paper closes your gap; compare its actual assumptions and experiment.

**Homework:** each student gives a ten-minute explanation of their closest assigned paper, followed by five minutes of questions. One teammate asks about the threat model; the other asks what experiment would change the conclusion. Keep a shared glossary of unfamiliar terms with your own examples.

**Checkpoint:** the team can state its difference from the closest work in two concrete sentences. “We apply it to 6G” needs an additional explanation of which network property changes the problem.

## 4. Set up a project that remembers what happened

Create a separate project directory inside RIVF after selecting the idea. Keep the accepted ATC and submitted ICLIE artifacts available as references. Record any reused component and its origin.

A small structure is sufficient. The following is a **suggested future layout**, not a set of files already created:

```text
selected_project/
  README.md
  environment/         dependency versions and machine notes
  configs/             saved experiment settings
  src/                 implementation
  scripts/             run, summarize, and plot entry points
  tests/               checks for the scientific assumptions
  notes/               reading notes, decisions, and workbook
  data/                dataset manifests and split identifiers
  results/raw/         original run outputs
  results/processed/   summaries derived from raw outputs
  figures/             generated figure files
  paper/               manuscript and references
```

Use version control for code, configuration, and notes. Keep large checkpoints and datasets in appropriate storage with recorded locations and checksums. Each experiment should identify the code revision, configuration, data split, model checkpoint, random seeds, machine, and software versions. If a run uses uncommitted changes, save the patch with it or commit the experiment state first.

The README should explain how to set up the environment and perform one small experiment. The run command must fail visibly if a required checkpoint or dataset is missing. Silent substitution with a random model or sample data can invalidate an entire evaluation.

Keep original outputs immutable. When you change an analysis script, produce a new summary from the same raw files. This lets you correct mistakes without losing the evidence needed to explain the correction.

**Checkpoint:** a teammate can reproduce the smallest run from your instructions without asking which button you clicked or which undocumented file you edited.

## 5. Reproduce a baseline before adding your idea

Your baseline is the reference against which later results will be interpreted. Establishing that it behaves correctly is one of the most valuable tasks in the project.

Start small enough to inspect individual examples. For a model experiment, print the checkpoint identifier, preprocessing, labels, predictions, and sample counts. For packet processing, trace the ownership of a few frames before generating millions of packets.

A candidate-specific starting point is:

- **Shard skew:** load an infected checkpoint, verify the attack, apply or load a documented repair, and confirm that the repaired model improves the intended outcome.
- **Precision exposure:** show that unsplit inference and split inference with an identity boundary agree within a stated numerical tolerance. Then validate each quantized boundary and test actual packing and reconstruction.
- **AF_XDP:** receive a bounded packet stream, account for all frames, and establish benign packet-delivery and inference measurements before adding attack traffic.

Agree on reproduction tolerance before judging the result. Exact agreement may be possible for deterministic composition on the same machine. Training or different hardware may produce variability. Explain expected differences and record actual ones.

When reproduction fails, change one thing at a time. Check data preprocessing, train/evaluation mode, full checkpoint state, label mapping, dependency versions, seed handling, metric denominator, and timing boundaries. Keep both the failed output and the eventual explanation.

**Checkpoint:** you can explain why your baseline result is credible. If you are still uncertain whether the baseline works, delay the proposed modification. Every later comparison depends on this foundation.

## 6. Construct the smallest experiment that could disprove the idea

You now have a baseline and a hypothesis. Design a pilot that isolates one cause.

For shard skew, write the four-stage model as `f(x) = f4(f3(f2(f1(x))))`. Begin with a repaired model whose full state is known. Replace exactly one stage with its historical state. Keep the same inputs, labels, evaluation mode, and other stages. Record how much of the repair was reverted.

A strong control is to repair several stages and then roll back only one. If the entire repair changed just the final classifier and you restore that classifier, you have effectively undone the complete repair. That observation can validate your code, but it does not establish the proposed interaction between remaining repaired and stale components.

For precision exposure, distinguish a state-specific attack from an advantage due to state information. Test the same eligible inputs with the same query and waiting budgets. A precision mode being easy to attack does not by itself show that the adaptive scheduler adds risk.

For AF_XDP, separate dequeue from reclamation. Temporarily retain frames after removing RX descriptors. Observe whether available FILL resources fall while RX occupancy remains small. Introduce controlled retention first; add realistic authentication or application delays once the mechanism is understood.

Write the pilot card **before** running it: question, changed variable, fixed conditions, controls, metrics, expected result, alternative explanation, and stop/continue criterion. The workbook contains the form.

Use the numerical gates in the scouting report to decide whether the effect is worth the remaining time. These thresholds select a project; they are not statistical proof of novelty or generality. Avoid repeatedly searching configurations until one passes and then presenting it as a preselected result. Label exploratory choices and confirm them on new data or runs.

**Checkpoint:** hold a day-5 meeting with the exact logs and one preliminary figure. Choose one of three actions: proceed with the bounded claim, debug a specific unresolved issue, or stop the candidate. Record the reason. An informative failure saves time for a better question.

## 7. Plan the full evidence before expanding the experiment matrix

Once the pilot is convincing, decide what a skeptical reader will need to see. Organize the evaluation around questions:

| Question | Experiment | Evidence to save |
|---|---|---|
| Does the effect exist? | Main comparison under matched conditions | Per-example or per-request outcomes and run summaries |
| What causes it? | One-component ablation or controlled intervention | Internal state showing the proposed cause |
| When does it matter? | One important sensitivity sweep | Performance across the relevant operating range |
| Does it survive a changed setting? | Second model, workload, trace, or machine configuration | Confirmation with the selection procedure frozen |
| What does protection cost? | Benign and attacked workload with mitigation | Utility, resource cost, lateness, rejection, and failures |

Choose comparisons that answer these questions. Include the simplest serious alternative and the closest practical prior method. If static policing plus reservation works just as well as your controller, that is a result the paper must address. If a fixed precision policy gives the same outcome at the same bandwidth cost, it is a necessary baseline.

Fairness needs explicit accounting. Match input sets, attacker information, query budgets, waiting time, hardware allocation, and tuning opportunities where they affect the conclusion. Count failed uploads, extra inference passes, retries, offline preparation, and recovery when your claim depends on their costs.

Use training data for fitting weights, validation/calibration data for thresholds and method selection, and a held-out evaluation set for the final comparison. Record their identifiers and avoid accidental duplicates across splits. Selecting the most vulnerable shard or burst pattern on final evaluation data turns that set into development data; use a new held-out set for confirmation or disclose the exploratory scope.

Count the planned runs before launching them. An **illustrative** matrix of two models, two attacks, two repairs, five configurations, and three seeds already requires 120 runs. At 15 minutes each, that is 30 serial hours before debugging or reruns. Time one representative run, then calculate the full cost including GPU memory, disk, preprocessing, and plotting.

Reduce an oversized matrix by preserving the comparisons that answer the main question. Add one confirmation setting and the most diagnostic ablation. Agree on this reduction with your supervisor while the evidence plan is still easy to change.

**Checkpoint:** by day 10, each planned figure answers a named research question, and the runs fit the remaining compute budget. Record which results are exploratory and which are confirmatory.

## 8. Measure outcomes so that another person can interpret them

Metrics need a numerator, denominator, unit, and measurement boundary. Writing these explicitly often reveals problems before the expensive runs begin.

For a targeted backdoor evaluation, define:

```text
ASR = eligible triggered examples predicted as the attacker target
      / all eligible triggered examples evaluated
```

State eligibility, including whether true target-class examples are excluded. Save raw counts as well as percentages. For adversarial examples, report the conventional overall robust-accuracy result where relevant, and separately report any analysis restricted to examples correct under every clean precision mode. Give the size of that restricted cohort. It helps isolate state effects but is not the full data distribution.

For a serving system, define:

```text
correct-and-on-time fraction = correct responses completed by the deadline
                              / all requests offered
```

For telemetry, use protected packets offered as the denominator of delivery success. A dropped packet has no observed delivery latency; it still counts as a delivery failure. Report latency among delivered packets alongside drops and deadline success so that a system cannot appear fast merely by discarding difficult work.

State where timing begins and ends. Distinguish model execution, serialization, transport, queueing, and full request latency. Account for asynchronous GPU execution when timing GPU work; time completion of the intended work rather than just its submission. For separate hosts, use a trustworthy clock arrangement or a same-clock round trip and explain what it measures. Keep warmup separate and record cold-start or recovery costs when those affect your claim.

A trace replay or simulator can be useful evidence. Label measured compute, measured traffic, injected delay, and model assumptions separately. An imposed bandwidth delay is not a measurement of a deployed 6G radio.

A percentile such as p99 describes the upper tail of the observations. Rare-tail estimates need enough observations and sufficiently long runs to cover relevant bursts. As an illustration, a run with 1,000 requests provides only about one observation above the 99.9th percentile. Prefer collecting more evidence or reporting a less extreme percentile over presenting a fragile tail claim.

### Repeat experiments at the level where randomness occurs

A seed identifies a random sequence. It may control initialization, data partitioning, attack search, or traffic generation. Log these separately when appropriate. Repeating the same checkpoint can measure evaluation randomness, but cannot estimate variability across independently trained models.

Use paired comparisons where possible: run baseline and proposed method on the same model seed, input cohort, and traffic trace. Compare the paired differences. For latency, also randomize or alternate execution order so that temperature or changing machine load does not consistently favor one method.

Here is a calculation using **fictional** results:

| Paired run | Baseline success | Proposed success | Difference |
|---|---:|---:|---:|
| 1 | 80% | 85% | +5 percentage points |
| 2 | 84% | 86% | +2 percentage points |
| 3 | 82% | 86% | +4 percentage points |

The mean paired improvement is 3.67 percentage points. Relative to the baseline mean of 82%, it is about 4.47%. These are different quantities. Report which one you use.

Include variation across independent runs, for example mean and standard deviation. A confidence interval addresses uncertainty in an estimate; it is different from standard deviation. Three runs are a pilot-sized starting point, and can leave wide uncertainty. If the conclusion depends on a small difference, allocate more runs or narrow the conclusion.

Millions of packets from a single burst trace are not millions of independent repetitions of the deployment. Preserve the run, episode, model, or traffic-session grouping when summarizing uncertainty. Ask your supervisor for help with an interval or resampling method that matches these dependencies.

**Checkpoint:** give a teammate a raw file and the metric definition. They should obtain the same summary without looking at the paper's proposed result.

## 9. Try to break your own explanation

An adversarial study needs an attacker that responds to the system being evaluated. Write what the attacker knows, then ask what it would change after seeing the mechanism. The methodological readings [On Evaluating Adversarial Robustness](https://arxiv.org/abs/1902.06705) and [On Adaptive Attacks to Adversarial Example Defenses](https://arxiv.org/abs/2002.08347) are useful guides to this stage.

For precision experiments, attack the actual quantized forward computation. Investigate failed gradients, increase search effort, use restarts, and include an independent attack approach where feasible. If attack success collapses precisely when gradients stop being informative, investigate the attack before interpreting the model as protected.

For shard skew, verify that the threat model matches the mitigation. A trusted loader can reject a historical artifact. A malicious runtime can lie about which weights it executed. Request metadata alone does not resolve that stronger threat.

For AF_XDP, let burst timing adapt to the feedback interval. Check buffer-accounting drift during receiver stalls and failed redirects. Verify whether the apparent benefit is explained by admitting fewer useful packets or receiving more CPU time.

Use a separate teaching question for each figure: “What else could cause this curve?” Examples include damaged baseline code, a changed data cohort, normalization mismatches, free attack queries, omitted drops, hidden retries, or extra resources. Design the smallest check that distinguishes your explanation from that alternative.

AI assistants can help identify counterexamples, inspect code, and formulate reviewer objections. Verify every suggested citation and numerical statement against the source. Keep a human owner for each experiment and claim. An AI review provides a useful challenge; its favorable verdict does not establish correctness.

**Checkpoint:** one student writes the strongest rejection paragraph they can. A second student points to the evidence that answers it. The third records objections that remain unresolved. Present those unresolved issues at the next supervisor meeting.

## 10. Turn the experiments into a scientific argument

Create a claim–evidence table before drafting the results section. Each row should contain a candidate statement, experiment identifier, raw output location, analysis script, numerical result, scope, and limitation. Mark unfinished rows as pending.

For example, a pending row might read:

> Proposed claim: one stale shard can restore attack behavior after a repair distributed across several shards. Evidence required: paired repaired/rollback comparisons, complete state checks, repair-update distribution, and confirmation across seeds. Status: pending measurements.

Choose figures by their role in that argument. For shard skew, a layer heatmap can show whether reactivation is concentrated in one stage. For precision exposure, a comparison across observation delays can establish how much information the attacker needs. For AF_XDP, a time series can align held frames, RX depth, bursts, and inference deadline misses.

Sketch the axes and comparison groups before the final runs. Leave results blank. This exercise tells you which fields to log. Never fill a draft with plausible numbers that might later be mistaken for measurements.

Generate final plots from saved data. Use readable axis labels and units, stable colors and markers, and matching axes for comparable panels. Check them at the intended column width. A caption should identify the comparison, conditions, and meaning of panels or error bars.

Write one result paragraph per question:

> We evaluated [question] by comparing [methods] under [conditions]. Changing [variable] produced [measured result with uncertainty]. The accompanying [ablation/internal measurement] supports [mechanism explanation]. The effect [changed/disappeared] under [boundary condition].

It is acceptable to write that an observation is “consistent with” an explanation when your evidence is indirect. Reserve stronger causal language for experiments that isolate the proposed cause.

If results are mixed, explain the boundary. A method working only above a certain burst duration or only at particular split points can still yield useful knowledge. Its value depends on whether that boundary is reproducible, nontrivial, and relevant to deployment.

**Checkpoint:** every headline statement has a row in the evidence table. Any unsupported statement is removed, narrowed, or marked as a hypothesis that still needs testing.

## 11. Write the six-page paper in a manageable order

Start the document in the first week with notes and section placeholders. Write the stable system model and experimental setup as soon as they are known. Complete the abstract and contribution statements after you understand the results.

A practical drafting order is: experimental setup, results and figures, mechanism or study method, threat model, related work, introduction, conclusion, abstract, and title. This order reduces the temptation to commit to findings before the evidence exists.

For planning, the [RIVF 2026 call](https://rivf2026.org/call-for-papers.html) specifies up to six pages in the IEEE A4 conference format. Budget references inside those six pages unless the organizer explicitly says otherwise. Confirm the selected track's deadline and anonymity instructions before submission; the earlier report records different main-track and SS3 deadline dates.

Here is a **suggested page budget**, including references:

| Content | Pages |
|---|---:|
| Title, author block if required, abstract, keywords | 0.40 |
| Introduction and contributions | 0.75 |
| Background and closest related work | 0.55 |
| System/threat model and mechanism or study design | 1.05 |
| Experimental setup | 0.55 |
| Results and their figures/tables | 1.70 |
| Limitations and conclusion | 0.25 |
| References | 0.75 |
| **Total** | **6.00** |

Adjust the allocation to the paper. A measurement study may devote more space to setup and controls. A protocol paper may need a short correctness argument. Keep enough room for a reader to understand the experiment independently of the artifact.

### Introduction

Begin with a concrete problem. For example:

> Edge inference services can update model shards independently. If an interrupted rollout mixes historical and repaired shards, the deployed computation differs from the complete model evaluated after repair.

Then explain the closest existing approaches and the specific question they leave open. State the system and attacker boundaries, the approach used to investigate the question, and two or three contributions supported by the evidence. Add the measured principal result only after it is verified.

### Method and threat model

Walk through one request or update in execution order. Define notation close to its first use. State which component checks each condition and what happens on failure. For a study, specify how interventions are constructed and which variables remain fixed.

A reader should be able to tell whether an old epoch is allowed to finish, whether a rejected request is retried, and whether an attacker can alter the runtime. Such details determine what the experiment establishes.

### Related work

Compare along the axis that matters. “Paper A uses technique B” is only the beginning. Continue with the question it answers and why your experiment is different. Cite the accepted ATC work when using its ideas or infrastructure, and discuss manuscript overlap with your supervisor.

### Abstract

Use a compact problem–approach–evidence progression. A fill-in template is:

> [Concrete problem] arises when [condition]. Existing [approaches/evaluations] leave [specific question] unresolved. We [study/build] [precise object] under [scope]. Using [implementation, data, and comparisons], we find [verified result] and [verified trade-off]. These results establish [bounded implication].

Do not claim a novel algorithm merely because you built new code. A strong empirical contribution can be described directly as a controlled study and its findings.

### Revision

Read the paper once for the argument, once for experimental completeness, and once for language and layout. Cut repeated motivation, broad background, and decorative diagrams before cutting settings necessary to reproduce the result. Preserve the template's margins and font sizes.

**Checkpoint:** give the draft to someone outside the project. Ask them to identify the problem, novelty, threat model, strongest finding, and main limitation. Their points of confusion are revision tasks.

## 12. Package the evidence and finish responsibly

Assign a teammate who did not write the main experiment to run the artifact from its instructions. Provide a quick smoke test and the full experiment path, with expected runtime, hardware, storage, data access, and output locations. If full reproduction takes many GPU hours, say so and provide a small example that exercises the same data flow.

Link every paper figure and table to its generating script and input manifest. Check that percentages, denominators, labels, and units agree across the abstract, text, tables, plots, and evidence table. Save the final code revision and exact submitted PDF together with the final run manifest.

Check every citation against the original source. For software and datasets, record versions and permitted distribution. Use supervised, isolated environments for attack experiments and obtain authorization before testing external systems. The candidate experiments can be conducted using controlled models, traffic, and local deployments.

Build the final PDF and inspect every page at normal reading size. Check figure text, references, equations, clipping, blank space, and the six-page limit. Ask all authors to approve the manuscript and confirm author order, affiliations, and submission requirements before uploading.

If an essential result is still unverified, tell your supervisor exactly what is missing. A documented research artifact and an honest decision to continue later are useful outcomes. A deadline does not turn an unresolved experiment into evidence.

## 13. Work as one team for three weeks

Use the candidate-specific role allocation from the scouting report, but make each result have an owner and a second reader. The person writing the experiment explains it to the person checking it. Share intermediate outputs daily so that writing does not become one student's last-minute burden.

At the end of each working day, write three sentences: what we learned, what remains uncertain, and what tomorrow's smallest decisive experiment is. Attach one run identifier, figure, or code change. “Worked on the model” does not tell teammates what they can rely on.

Keep supervisor meetings short and evidence-centered. Bring one result, one interpretation, one unresolved question, and your recommended next action. If a reproduction is blocked, bring the smallest failing example and the checks you have already performed.

The schedule below is a default; actual checkpoints take precedence over calendar optimism.

| Day | Main task | Concrete output |
|---|---|---|
| 1 | Choose and scope one idea; check resources and submission rules | One-page project agreement |
| 2 | Read closest work; divide implementation responsibilities | Literature matrix and terminology sheet |
| 3 | Reproduce a baseline and define measurement contracts | Reproduction record and working small run |
| 4 | Validate the intervention and controls | Pilot experiment card and raw outcomes |
| 5 | Discuss the pilot with the supervisor | Recorded proceed/debug/stop decision |
| 6–7 | Strengthen attacks or failure tests; resolve confounders | Repeatable pilot and candidate-specific gate result |
| 8–9 | Implement necessary mechanism and closest baselines | Controlled comparison with resource accounting |
| 10 | Freeze main design and full evaluation plan | Run matrix, cost estimate, and planned figures |
| 11–13 | Run primary experiments and ablations | Raw results and validated analysis |
| 14–15 | Confirm in a second setting and test failure boundaries | Claim–evidence table with supported scope |
| 16–17 | Complete the manuscript argument | Full draft and generated figures |
| 18 | Conduct adversarial review | Objections linked to evidence or required revision |
| 19 | Reproduce independently and correct inconsistencies | Artifact verification record |
| 20 | Revise language, citations, and layout | Author-review PDF |
| 21 | Obtain final author approval and submit if ready | Submission package and archived experiment state |

If a candidate fails on day 5, use the remaining time with your supervisor's revised plan. Do not assume a second idea can automatically be completed in the original three-week window. Its prerequisites and pilot still need to work.

Plan demanding experiments while someone is available to observe their first outputs. Use unattended runs for configurations already checked. Protect enough rest that the team can reason about unexpected results; fatigue is especially costly when it changes a metric definition or hides a failed run.

## 14. When you feel stuck

| What is happening | A useful next step |
|---|---|
| “I do not understand the paper.” | Explain one figure and list the undefined terms that prevent you from interpreting it. Read those concepts next. |
| “The baseline disagrees with the paper.” | Save the mismatch, compare settings, and inspect a few examples before scaling. |
| “Our method loses.” | Check validity and resource matching, then investigate where and why it loses. Keep the result. |
| “All attacks fail.” | Verify the attack implementation and its access to the actual system before interpreting defense strength. |
| “Results vary across runs.” | Identify which source of randomness changes; preserve paired comparisons and increase independent repetitions where needed. |
| “There are too many experiments.” | Map each run to a research question and remove runs that do not resolve an uncertainty. |
| “Our idea is already published.” | Write the exact overlap and discuss whether a meaningful unanswered question remains. |
| “The paper is eight pages.” | Remove repeated background and redundant plots; retain threat-model details, decisive controls, and references. |
| “We have code but no paper.” | Write the three most defensible findings, identify their evidence, and build the results section around them. |

Begin with the first page of the workbook. Complete it together, choose the smallest experiment, and make its outcome inspectable. That gives you something concrete to discuss, even while many aspects of the project remain uncertain.
