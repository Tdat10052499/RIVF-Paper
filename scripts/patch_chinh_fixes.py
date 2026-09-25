#!/usr/bin/env python3
"""
scripts/patch_chinh_fixes.py
Apply all Chinh-responsibility fixes from Dat's 25/09/2026 review note.

Changes to paper/main.tex
  1a. ANP description: replace internal script path with prose + cite
  1b. ANP table caption: replace config file path with prose + cite
  1c. Partition section: drop "implemented in src/partition/shard.py"
  1d. substitute() signature: replace with prose description
  2.  ANP coverage (§3.6): qualify "regardless of which shard" -> tested 4
  3.  fig:locality_asr caption: remove shard-4 ASR claim (factual error)
  4a. CIFAR-10 citation: add krizhevsky2009cifar alongside backdoorbench2024
  4b. PreActResNet citation: add he2016identity alongside backdoorbench2024
  4c. BadNets citation: add gu2019badnets alongside backdoorbench2024

Changes to paper/references.bib
  Add krizhevsky2009cifar, gu2019badnets, he2016identity entries

Usage:
    cd RIVF-Paper
    python scripts/patch_chinh_fixes.py
    git add paper/main.tex paper/references.bib
    git commit -m "Fix: Chinh items from Dat 25/09 review (caption, wording, citations)"
    git push
"""

import re
import os
import sys

MAIN_TEX = os.path.join("paper", "main.tex")
REFS_BIB = os.path.join("paper", "references.bib")

# -----------------------------------------------------------------------
def patch_main_tex():
    with open(MAIN_TEX, "rb") as f:
        raw = f.read()
    crlf = b"\r\n" in raw
    text = raw.replace(b"\r\n", b"\n").decode("utf-8")

    issues = []
    applied = []

    # ---- 1a: Remove internal ANP script path ----
    m = re.search(
        r"We apply ANP\s+"
        r"via BackdoorBench's own \\texttt\{defense/anp\.py\} defense script,\s+"
        r"without any modification\.",
        text
    )
    if m:
        text = (text[:m.start()] +
                "We apply ANP\nusing BackdoorBench's reference\n"
                "implementation~\\cite{backdoorbench2024}, without modification." +
                text[m.end():])
        applied.append("1a: ANP script path -> prose")
    else:
        issues.append("1a (ANP script path): pattern not found")

    # ---- 1b: ANP table caption - remove config file path ----
    OLD_CAP = "\\caption{ANP defense configuration (BackdoorBench, \\texttt{config/defense/anp/cifar10.yaml})}"
    NEW_CAP = "\\caption{ANP defense configuration, following BackdoorBench's default CIFAR-10 settings~\\cite{backdoorbench2024}.}"
    if OLD_CAP in text:
        text = text.replace(OLD_CAP, NEW_CAP, 1)
        applied.append("1b: ANP table caption config path -> prose")
    else:
        issues.append("1b (ANP table caption): pattern not found")

    # ---- 1c: Partition - drop "implemented in src/partition/shard.py" ----
    OLD_SHARD = "and $n\\!=\\!6$ (fine), implemented in \\texttt{src/partition/shard.py}."
    NEW_SHARD = "and $n\\!=\\!6$ (fine)."
    if OLD_SHARD in text:
        text = text.replace(OLD_SHARD, NEW_SHARD, 1)
        applied.append("1c: shard.py path removed")
    else:
        issues.append("1c (shard.py path): pattern not found")

    # ---- 1d: substitute() function signature -> prose ----
    m = re.search(
        r"The \\texttt\{substitute\(model,\s*shard\\_id,\s*stale\\_weights\)\}\s+function\s+"
        r"replaces the parameters of the specified shard in an otherwise-repaired\s+"
        r"model with weights from the pre-repair \(infected\) checkpoint, leaving\s+"
        r"all other shards untouched\.",
        text, re.DOTALL
    )
    if m:
        text = (text[:m.start()] +
                "The substitution procedure replaces the parameters of the specified shard\n"
                "in an otherwise-repaired model with weights from the pre-repair (infected)\n"
                "checkpoint, leaving all other shards untouched." +
                text[m.end():])
        applied.append("1d: substitute() signature -> prose")
    else:
        issues.append("1d (substitute() signature): pattern not found")

    # ---- 2: ANP coverage qualifier (§3.6) ----
    OLD_QUAL = "CIFAR-10---regardless of which shard is substituted."
    NEW_QUAL = "CIFAR-10---in each of the four shards tested individually."
    if OLD_QUAL in text:
        text = text.replace(OLD_QUAL, NEW_QUAL, 1)
        applied.append("2: ANP coverage qualifier qualified")
    else:
        issues.append("2 (ANP coverage qualifier): pattern not found")

    # ---- 3: fig:locality_asr caption - remove shard-4 ASR claim ----
    m = re.search(
        r"\\emph\{Fine-tune\} \(circles\): the two highest-share shards\s+"
        r"\(\$\\sigma_3\{=\}47\.74\\%\$,\s*\$\\sigma_4\{=\}24\.29\\%\$\) produce\s+"
        r"single-shard ASRs of \$0\.50\\%\$ and below;\s+"
        r"three shards must be\s+substituted together to cross the \$90\\%\$ ASR threshold\s+"
        r"\(Section~\\ref\{sec:kcurve\}\)\.",
        text, re.DOTALL
    )
    if m:
        text = (text[:m.start()] +
                "\\emph{Fine-tune} (circles): even the highest-share shard\n"
                "    ($\\sigma_3{=}47.74\\%$) yields a single-shard ASR of only\n"
                "    $0.50\\%$; three shards must be substituted together to\n"
                "    cross the $90\\%$ ASR threshold (Section~\\ref{sec:kcurve})." +
                text[m.end():])
        applied.append("3: locality_asr caption shard-4 claim removed (factual fix)")
    else:
        issues.append("3 (locality_asr caption): pattern not found")

    # ---- 4a: CIFAR-10 original citation ----
    OLD_C10 = "CIFAR-10~\\cite{backdoorbench2024}, comprising"
    NEW_C10 = "CIFAR-10~\\cite{krizhevsky2009cifar,backdoorbench2024}, comprising"
    if OLD_C10 in text:
        text = text.replace(OLD_C10, NEW_C10, 1)
        applied.append("4a: CIFAR-10 citation -> krizhevsky2009cifar added")
    elif "krizhevsky2009cifar" in text:
        applied.append("4a: CIFAR-10 citation already updated, skipped")
    else:
        issues.append("4a (CIFAR-10 citation): pattern not found")

    # ---- 4b: PreActResNet18 original citation ----
    OLD_RN = "PreActResNet18~\\cite{backdoorbench2024}, a"
    NEW_RN = "PreActResNet18~\\cite{he2016identity,backdoorbench2024}, a"
    if OLD_RN in text:
        text = text.replace(OLD_RN, NEW_RN, 1)
        applied.append("4b: PreActResNet citation -> he2016identity added")
    elif "he2016identity" in text:
        applied.append("4b: PreActResNet citation already updated, skipped")
    else:
        issues.append("4b (PreActResNet citation): pattern not found")

    # ---- 4c: BadNets original citation ----
    OLD_BN = "We apply BadNets~\\cite{backdoorbench2024}"
    NEW_BN = "We apply BadNets~\\cite{gu2019badnets,backdoorbench2024}"
    if OLD_BN in text:
        text = text.replace(OLD_BN, NEW_BN, 1)
        applied.append("4c: BadNets citation -> gu2019badnets added")
    elif "gu2019badnets" in text:
        applied.append("4c: BadNets citation already updated, skipped")
    else:
        issues.append("4c (BadNets citation): pattern not found")

    # Count remaining todos
    todo_count = len(re.findall(r"\\todo\{", text))

    if crlf:
        text = text.replace("\n", "\r\n")

    with open(MAIN_TEX, "w", encoding="utf-8") as f:
        f.write(text)

    print("=== main.tex patches ===")
    for a in applied:
        print(f"  OK  {a}")
    for iss in issues:
        print(f"  WARN {iss}")
    print(f"Remaining \\todo blocks: {todo_count}")
    return len(issues) == 0


# -----------------------------------------------------------------------
def patch_refs_bib():
    with open(REFS_BIB, "rb") as f:
        raw = f.read()
    crlf = b"\r\n" in raw
    text = raw.replace(b"\r\n", b"\n").decode("utf-8")

    if "krizhevsky2009cifar" in text:
        print("\n=== references.bib ===")
        print("  SKIP original-source entries already present")
        return True

    new_entries = (
        "\n% -- Original-source citations added 25/09/2026 (Chinh, per Dat review) --\n"
        "\n"
        "@techreport{krizhevsky2009cifar,\n"
        "  title        = {Learning Multiple Layers of Features from Tiny Images},\n"
        "  author       = {Krizhevsky, Alex and Hinton, Geoffrey},\n"
        "  institution  = {University of Toronto},\n"
        "  year         = {2009},\n"
        "  note         = {Available at \\url{https://www.cs.toronto.edu/~kriz/cifar.html}},\n"
        "}\n"
        "\n"
        "@article{gu2019badnets,\n"
        "  title        = {{BadNets}: Identifying Vulnerabilities in the Machine\n"
        "                  Learning Model Supply Chain},\n"
        "  author       = {Gu, Tianyu and Dolan-Gavitt, Brendan and Garg, Siddharth},\n"
        "  journal      = {IEEE Access},\n"
        "  year         = {2019},\n"
        "  note         = {arXiv:1708.06733},\n"
        "}\n"
        "\n"
        "@inproceedings{he2016identity,\n"
        "  title        = {Identity Mappings in Deep Residual Networks},\n"
        "  author       = {He, Kaiming and Zhang, Xiangyu and Ren, Shaoqing and Sun, Jian},\n"
        "  booktitle    = {European Conference on Computer Vision (ECCV)},\n"
        "  year         = {2016},\n"
        "  note         = {arXiv:1603.05027},\n"
        "}\n"
    )

    text = text.rstrip("\n") + "\n" + new_entries

    if crlf:
        text = text.replace("\n", "\r\n")

    with open(REFS_BIB, "w", encoding="utf-8") as f:
        f.write(text)

    print("\n=== references.bib ===")
    print("  OK  added: krizhevsky2009cifar, gu2019badnets, he2016identity")
    return True


# -----------------------------------------------------------------------
if __name__ == "__main__":
    ok_tex = patch_main_tex()
    ok_bib = patch_refs_bib()
    print()
    if ok_tex and ok_bib:
        print("All patches applied cleanly.")
        print("Next steps:")
        print("  git add paper/main.tex paper/references.bib")
        print('  git commit -m "Fix: Chinh items from Dat 25/09 review (caption, wording, citations)"')
        print("  git push")
    else:
        print("Some patterns were not found -- review WARNings above before committing.")
        sys.exit(1)
