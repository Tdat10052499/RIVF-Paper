"""patch_tikz_figure.py
Replace the \\includegraphics figure in §4.7 (locality_vs_asr.pdf)
with an inline pgfplots TikZ scatter plot.

Usage (PowerShell, from repo root):
    git pull
    python scripts/patch_tikz_figure.py
    git add paper/main.tex
    git commit -m "Fig 4.7: replace includegraphics with inline pgfplots TikZ scatter"
    git push
"""

import re, sys
from pathlib import Path

TEX = Path("paper/main.tex")

OLD = r"""\begin{figure}[t]
  \centering
  \includegraphics[width=\columnwidth]{locality_vs_asr.pdf}
  \caption{Repair locality vs.\\ rollback vulnerability.
    Each marker is one shard.
    \emph{Fine-tune} (circles): the two highest-share shards
    ($\sigma_3{=}47.74\%$, $\sigma_4{=}24.29\%$) produce
    single-shard ASRs of $0.50\%$ and below; three shards must be
    substituted together to cross the $90\%$ ASR threshold
    (Section~\ref{sec:kcurve}).
    \emph{ANP} (triangles): shard~5 ($\sigma_5{=}2.92\%$) registers
    $\text{ASR}=81.10\%$, but this is a utility-collapse artifact
    ($\text{CA}=10\%$) rather than genuine backdoor recovery
    (Section~\ref{sec:anp}).}
  \label{fig:locality_asr}
\end{figure}"""

NEW = r"""\begin{figure}[t]
  \centering
  \begin{tikzpicture}
  \begin{axis}[
      width=\columnwidth,
      height=5.8cm,
      xlabel={Repair share $\sigma_s$ (\%)},
      ylabel={Single-shard rollback ASR (\%)},
      xmin=-5, xmax=55,
      ymin=-8, ymax=95,
      xtick={0,10,20,30,40,50},
      ytick={0,20,40,60,80},
      tick label style={font=\small},
      label style={font=\small},
      legend style={at={(0.97,0.97)}, anchor=north east, font=\small},
      grid=major,
      grid style={dashed, gray!30},
      every axis plot/.append style={thick},
  ]
  %% Fine-tune points (circles, blue)
  %% Shard 0: sigma=0.30, ASR=1.02
  %% Shard 2: sigma=21.11, ASR=8.94
  %% Shard 3: sigma=47.74, ASR=0.50
  %% Shard 5: sigma=0.13, ASR=1.18
  \addplot[
      only marks, mark=*, mark size=3pt,
      color=blue!70!black,
  ] coordinates {
      (0.30,  1.02)
      (21.11, 8.94)
      (47.74, 0.50)
      (0.13,  1.18)
  };
  \addlegendentry{Fine-tune}

  %% ANP points (triangles, red)
  %% Shard 0: sigma=2.02, ASR=0.00
  %% Shard 2: sigma=19.31, ASR=0.00
  %% Shard 3: sigma=33.66, ASR=0.00
  %% Shard 5: sigma=2.92, ASR=81.10 (utility-collapse artifact)
  \addplot[
      only marks, mark=triangle*, mark size=3pt,
      color=red!70!black,
  ] coordinates {
      (2.02,  0.00)
      (19.31, 0.00)
      (33.66, 0.00)
      (2.92, 81.10)
  };
  \addlegendentry{ANP}

  %% Shard labels -- fine-tune
  \node[font=\scriptsize, blue!70!black, anchor=south west]
      at (axis cs:0.30,  1.02) {$s_0$};
  \node[font=\scriptsize, blue!70!black, anchor=south west]
      at (axis cs:21.11, 8.94) {$s_2$};
  \node[font=\scriptsize, blue!70!black, anchor=south east]
      at (axis cs:47.74, 0.50) {$s_3$};
  \node[font=\scriptsize, blue!70!black, anchor=south east]
      at (axis cs:0.13,  1.18) {$s_5$};

  %% Shard labels -- ANP
  \node[font=\scriptsize, red!70!black, anchor=north east]
      at (axis cs:2.02,  0.01) {$s_0$};
  \node[font=\scriptsize, red!70!black, anchor=north west]
      at (axis cs:19.31, 0.01) {$s_2$};
  \node[font=\scriptsize, red!70!black, anchor=north east]
      at (axis cs:33.66, 0.01) {$s_3$};
  \node[font=\scriptsize, red!70!black, anchor=west]
      at (axis cs:2.92, 81.10) {\;$s_5$ (artifact)};

  \end{axis}
  \end{tikzpicture}
  \caption{Repair locality vs.\\ rollback vulnerability.
    Each marker is one shard.
    \emph{Fine-tune} (circles): the two highest-share shards
    ($\sigma_3{=}47.74\%$, $\sigma_4{=}24.29\%$) produce
    single-shard ASRs of $0.50\%$ and below; three shards must be
    substituted together to cross the $90\%$ ASR threshold
    (Section~\ref{sec:kcurve}).
    \emph{ANP} (triangles): shard~5 ($\sigma_5{=}2.92\%$) registers
    $\text{ASR}=81.10\%$, but this is a utility-collapse artifact
    ($\text{CA}=10\%$) rather than genuine backdoor recovery
    (Section~\ref{sec:anp}).}
  \label{fig:locality_asr}
\end{figure}"""


def main():
    if not TEX.exists():
        sys.exit(f"ERROR: {TEX} not found. Run from repo root.")

    raw = TEX.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")

    if OLD not in text:
        print("WARNING: expected figure block not found -- already patched or tex changed.")
        print("Searching for \\includegraphics{locality_vs_asr.pdf} ...")
        if r"\includegraphics[width=\columnwidth]{locality_vs_asr.pdf}" in text:
            print("  Found includegraphics line but surrounding block differs.")
            print("  Patch NOT applied. Please apply manually.")
        else:
            print("  Not found at all -- file may already use TikZ.")
        sys.exit(1)

    patched = text.replace(OLD, NEW, 1)
    if crlf:
        patched = patched.replace("\n", "\r\n")
    TEX.write_bytes(patched.encode("utf-8"))
    print("OK: locality figure replaced with inline pgfplots TikZ scatter plot.")

    # Count remaining todos
    n = patched.count(r"\todo{")
    print(f"Remaining \\todo blocks: {n}")


if __name__ == "__main__":
    main()
