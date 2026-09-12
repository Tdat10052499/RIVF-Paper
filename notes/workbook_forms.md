# Student Research Workbook Forms

Use this with the [zero-to-one tutorial](student_zero_to_one_tutorial.md). Copy the forms into the selected project's notes and complete them as evidence becomes available. Angle-bracket fields are placeholders. No experiment has been run by completing this template.

---

## B. Reading note — one per close source

```
Exact title / authors / year / venue or preprint status:
Primary-source URL and version/date accessed:
Reader:

Question answered by the paper:
Threat/system assumptions:
Mechanism in my own words:
Strongest evidence, with section/table/figure:
Closest baseline and fairness of comparison:
Known limitations:
Difference from our proposed study:
Code/data availability and dependency concerns:
One question to ask my teammates:
```

---

## C. Reproduction record — before the proposed intervention

```
Reference experiment and source location:
Expected outcome and acceptable variation:
Code repository and pinned revision:
Changes from the reference implementation:
Environment and hardware:
Dataset version, split identifiers, and preprocessing:
Checkpoint identifier, origin, and checksum:
Model parameters AND persistent buffers included:
Run command and configuration:
Random seeds and their roles:
Timing boundary and warmup:
Raw-output path:

Observed outcome and sample counts:
Difference from reference:
Checks performed to explain the difference:
Remaining uncertainty:
Second reader and verification date:
```

---

## D. Experiment card — write before running

```
Experiment ID:
Owner / second reader:
Exploratory or confirmatory:
Research question and hypothesis:

Changed variable and values:
Fixed conditions:
Baseline(s):
Control(s) ruling out alternative explanations:
Attacker information and budget for each method:
Matched resources and any unavoidable differences:
Dataset/model/trace selection rule:
Metric formulas, units, and denominators:
Independent repetition unit:
Seed list / pairing / execution order:
Analysis and uncertainty-reporting plan:
Failure/timeout handling:
Pilot duration and estimated total cost:

Expected outcome if the hypothesis is correct:
Outcome that would refute or weaken it:
Predeclared continue/stop criterion:
Raw fields required for the planned figure:
```

---

## E. Run record — save with every run

```json
{
  "run_id": "<unique-id>",
  "experiment_id": "<experiment-card-id>",
  "status": "<completed|failed|timed_out>",
  "code_revision": "<commit-id>",
  "uncommitted_patch_path": null,
  "config_path": "<saved-config>",
  "environment_path": "<dependency-and-machine-record>",
  "data_manifest_path": "<split-and-source-manifest>",
  "checkpoint_digest": "<digest-or-not-applicable>",
  "seeds": {},
  "started_at": "<timestamp-with-timezone>",
  "finished_at": "<timestamp-with-timezone>",
  "counts": {},
  "metrics": {},
  "raw_events_path": "<per-example-or-per-request-log>",
  "warnings": [],
  "failure_reason": null
}
```

Replace placeholders with actual values. Define the schema of counts, metrics, and raw events in the experiment card. Do not encode missing measurements as zero or silently exclude unsuccessful runs.

---

## F. Claim-evidence table — maintain during analysis

| Claim ID | Exact proposed sentence | Experiment/run IDs | Raw evidence and analysis script | Estimate and uncertainty | Scope and counterevidence | Status / second reader |
|---|---|---|---|---|---|---|
| C1 | bounded claim | IDs | paths | pending | conditions and failures | Pending |

Use statuses such as proposed, measured, independently checked, narrowed, or removed. A hypothesis that passes a pilot is still subject to confirmation.

---

## G. Day-5 or day-10 decision

```
Decision date and checkpoint:
Evidence considered, including failed runs:
Does the baseline work? Evidence:
Does the key effect meet the predeclared gate? Evidence:
Strongest surviving alternative explanation:
Closest-work overlap still unresolved:
Remaining compute/time requirements:

Decision: proceed / debug a named issue / narrow / stop
Reason:
Approved claim scope:
Next experiment and owner:
Next decision date:
Supervisor feedback:
```

---

## H. Daily team note

```
Date:
What we learned:
Evidence: run ID, figure, or code revision
What remains uncertain:
Tomorrow's smallest decisive experiment:
Owner and second reader:
Help needed, with smallest reproducible example:
```

---

## I. Review response log

| Objection | Why it could invalidate the claim | Evidence or required experiment | Revision and owner | Resolved? |
|---|---|---|---|---|
| reviewer concern | consequence | evidence/path or planned test | change | No |

---

## J. Manuscript and artifact handoff

- [ ] Main question, contributions, and limitations agree across the paper.
- [ ] Every headline number maps to a checked claim-evidence row.
- [ ] Main baselines, attack budgets, data splits, denominators, and uncertainty are documented.
- [ ] Failed, late, dropped, and rejected cases are accounted for where relevant.
- [ ] Reused methods, software, and prior papers are attributed; overlap is reviewed with the supervisor.
- [ ] Dataset/model provenance and distribution conditions are recorded.
- [ ] A teammate has run the smoke test and checked at least one headline result from the instructions.
- [ ] Figure/table generation paths and full-run resource requirements are documented.
- [ ] References were checked against primary sources.
- [ ] The final PDF was visually inspected and meets the verified venue rules.
- [ ] All authors approved the final manuscript and submission details.
- [ ] Submitted PDF, code revision, configurations, and evidence manifest are archived together.
