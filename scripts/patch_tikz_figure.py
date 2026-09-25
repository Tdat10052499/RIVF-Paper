"""patch_tikz_figure.py
Replace the \includegraphics figure in §4.7 (locality_vs_asr.pdf)
with an inline pgfplots TikZ scatter plot.

Usage (PowerShell, from repo root):
    git pull
    python scripts/patch_tikz_figure.py
    git add paper/main.tex
    git commit -m "Fig 4.7: replace includegraphics with inline pgfplots TikZ scatter"
    git push
"""

import re
import sys
from pathlib import Path

TEX = Path("paper/main.tex")

# New TikZ figure block (replaces the includegraphics block)
NEW_FIGURE = (
    "\\begin{figure}[t]\n"
    "  \\centering\n"
    "  \\begin{tikzpicture}\n"
    "  \\begin{axis}[\n"
    "      width=\\columnwidth,\n"
    "      height=5.8cm,\n"
    "      xlabel={Repair share $\\sigma_s$ (\\%)},\n"
    "      ylabel={Single-shard rollback ASR (\\%)},\n"
    "      xmin=-5, xmax=55,\n"
    "      ymin=-8, ymax=95,\n"
    "      xtick={0,10,20,30,40,50},\n"
    "      ytick={0,20,40,60,80},\n"
    "      tick label style={font=\\small},\n"
    "      label style={font=\\small},\n"
    "      legend style={at={(0.97,0.97)}, anchor=north east, font=\\small},\n"
    "      grid=major,\n"
    "      grid style={dashed, gray!30},\n"
    "      every axis plot/.append style={thick},\n"
    "  ]\n"
    "  %% Fine-tune (circles, blue): repair-share sigma vs single-shard ASR\n"
    "  %% s0: sigma=0.30, ASR=1.02 | s2: sigma=21.11, ASR=8.94\n"
    "  %% s3: sigma=47.74, ASR=0.50 | s5: sigma=0.13, ASR=1.18\n"
    "  \\addplot[\n"
    "      only marks, mark=*, mark size=3pt,\n"
    "      color=blue!70!black,\n"
    "  ] coordinates {\n"
    "      (0.30,  1.02)\n"
    "      (21.11, 8.94)\n"
    "      (47.74, 0.50)\n"
    "      (0.13,  1.18)\n"
    "  };\n"
    "  \\addlegendentry{Fine-tune}\n"
    "\n"
    "  %% ANP (triangles, red): repair-share sigma vs single-shard ASR\n"
    "  %% s0: sigma=2.02, ASR=0.00 | s2: sigma=19.31, ASR=0.00\n"
    "  %% s3: sigma=33.66, ASR=0.00 | s5: sigma=2.92, ASR=81.10 (utility-collapse artifact)\n"
    "  \\addplot[\n"
    "      only marks, mark=triangle*, mark size=3pt,\n"
    "      color=red!70!black,\n"
    "  ] coordinates {\n"
    "      (2.02,  0.00)\n"
    "      (19.31, 0.00)\n"
    "      (33.66, 0.00)\n"
    "      (2.92, 81.10)\n"
    "  };\n"
    "  \\addlegendentry{ANP}\n"
    "\n"
    "  %% Shard labels -- fine-tune\n"
    "  \\node[font=\\scriptsize, blue!70!black, anchor=south west]\n"
    "      at (axis cs:0.30,  1.02) {$s_0$};\n"
    "  \\node[font=\\scriptsize, blue!70!black, anchor=south west]\n"
    "      at (axis cs:21.11, 8.94) {$s_2$};\n"
    "  \\node[font=\\scriptsize, blue!70!black, anchor=south east]\n"
    "      at (axis cs:47.74, 0.50) {$s_3$};\n"
    "  \\node[font=\\scriptsize, blue!70!black, anchor=south east]\n"
    "      at (axis cs:0.13,  1.18) {$s_5$};\n"
    "\n"
    "  %% Shard labels -- ANP\n"
    "  \\node[font=\\scriptsize, red!70!black, anchor=north east]\n"
    "      at (axis cs:2.02,  0.01) {$s_0$};\n"
    "  \\node[font=\\scriptsize, red!70!black, anchor=north west]\n"
    "      at (axis cs:19.31, 0.01) {$s_2$};\n"
    "  \\node[font=\\scriptsize, red!70!black, anchor=north east]\n"
    "      at (axis cs:33.66, 0.01) {$s_3$};\n"
    "  \\node[font=\\scriptsize, red!70!black, anchor=west]\n"
    "      at (axis cs:2.92, 81.10) {\\;$s_5$ (artifact)};\n"
    "\n"
    "  \\end{axis}\n"
    "  \\end{tikzpicture}\n"
    "  \\caption{Repair locality vs.\\ rollback vulnerability.\n"
    "    Each marker is one shard.\n"
    "    \\emph{Fine-tune} (circles): the two highest-share shards\n"
    "    ($\\sigma_3{=}47.74\\%$, $\\sigma_4{=}24.29\\%$) produce\n"
    "    single-shard ASRs of $0.50\\%$ and below; three shards must be\n"
    "    substituted together to cross the $90\\%$ ASR threshold\n"
    "    (Section~\\ref{sec:kcurve}).\n"
    "    \\emph{ANP} (triangles): shard~5 ($\\sigma_5{=}2.92\\%$) registers\n"
    "    $\\text{ASR}=81.10\\%$, but this is a utility-collapse artifact\n"
    "    ($\\text{CA}=10\\%$) rather than genuine backdoor recovery\n"
    "    (Section~\\ref{sec:anp}).}\n"
    "  \\label{fig:locality_asr}\n"
    "\\end{figure}"
)


def main():
    if not TEX.exists():
        sys.exit(f"ERROR: {TEX} not found. Run from repo root.")

    raw = TEX.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")

    # Find the figure block that contains locality_vs_asr.pdf using regex
    pattern = re.compile(
        r"\\begin\{figure\}\[t\].*?locality_vs_asr\.pdf.*?\\end\{figure\}",
        re.DOTALL
    )

    match = pattern.search(text)
    if not match:
        print("WARNING: could not find a figure block containing locality_vs_asr.pdf")
        print("Checking for the includegraphics line directly...")
        if "locality_vs_asr.pdf" in text:
            print("  Found locality_vs_asr.pdf in file but regex failed.")
            print("  Please check the figure block manually.")
        else:
            print("  locality_vs_asr.pdf not found at all -- may already be patched.")
        sys.exit(1)

    patched = text[:match.start()] + NEW_FIGURE + text[match.end():]

    if crlf:
        patched = patched.replace("\n", "\r\n")
    TEX.write_bytes(patched.encode("utf-8"))
    print("OK: locality figure replaced with inline pgfplots TikZ scatter plot.")

    n = patched.count("\\todo{")
    print(f"Remaining \\todo blocks: {n}")


if __name__ == "__main__":
    main()
