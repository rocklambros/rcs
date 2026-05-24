# The four-part template per step

Every step in a walkthrough uses these four parts, in this order. Skipping any part degrades the walkthrough's pedagogical value in a specific, predictable way.

## The template

```markdown
## Step N: <one-line label naming the decision or computation>

- **What it's asking:** <restate the question in the student's vocabulary at the appropriate tier>
- **Why this works:** <name the principle, theorem, method, or rule being applied>
- **What the result tells us:** <interpret the output back into the original problem's language>
- **Gotcha:** <name the predictable failure mode at THIS step, sourced from observed errors>
```

## What each part does (and what breaks if you skip it)

| Part | Purpose | What breaks if skipped |
|---|---|---|
| What it's asking | Translates the problem into the student's current vocabulary; surfaces ambiguity | Student executes mechanics without understanding the question; can solve copies but not variations |
| Why this works | Names the transferable principle | Student memorizes the answer; cannot apply to next problem; bombs the exam variation |
| What the result tells us | Closes the loop from numerical output back to the question | Student computes a correct p-value or test statistic but cannot interpret it; "stats illiteracy" symptom |
| Gotcha | Inoculates against the predictable failure mode | Student walks into the canonical mistake at exam time even though the walkthrough technically covered the topic |

## Worked example: paired non-Normal stats problem (5-step)

### Step 1: Read the design

- **What it's asking:** is the data one-group, paired, or independent two-group? This determines the test family.
- **Why this works:** the design dictates the test family before any numbers are computed.
- **What the result tells us:** before / after on the SAME 24 patients → paired (one-group on the differences).
- **Gotcha:** new students often see two columns (before, after) and code a two-sample t-test. The two columns belong to the same person — paired.

### Step 2: Check the gating assumption

- **What it's asking:** are the differences Normally distributed? (Required for the paired t-test.)
- **Why this works:** parametric tests assume Normality; violating it invalidates the reported p-value.
- **What the result tells us:** Shapiro-Wilk p = 0.018 < α = 0.05 → reject Normality of the differences.
- **Gotcha:** students often run Shapiro on the before column AND the after column. For paired tests, Shapiro runs on the DIFFERENCES.

### Step 3: Pick the test

- **What it's asking:** which paired test handles non-Normal data?
- **Why this works:** when the assumption for the parametric variant fails, switch to the non-parametric variant in the same family.
- **What the result tells us:** Wilcoxon signed-rank is the paired non-parametric test.
- **Gotcha:** students often default to paired t even after the Shapiro rejects Normality. The whole point of the assumption check is to gate the choice.

### Step 4: Run and report

- **What it's asking:** what does the test produce and which numbers go in the report?
- **Why this works:** a hypothesis test answers a yes/no question at a stated α; report the test statistic + p + the decision.
- **What the result tells us:** V = <value>, p = <value>; compare to α = 0.05.
- **Gotcha:** students sometimes report the t-statistic for a Wilcoxon, or report p only without the test statistic. Both belong in the report.

### Step 5: Effect size + interpretation

- **What it's asking:** how big is the change, and what does that mean clinically?
- **Why this works:** p answers significance; effect size answers magnitude. Both are required.
- **What the result tells us:** rank-biserial r (or Cliff's δ) with 95% CI; interpret in cholesterol-lowering language ("median reduction of X mg/dL").
- **Gotcha:** reporting only p without effect size is the single most common write-up failure (see `reporting-effect-sizes` skill).

## Worked example: longest common subsequence (DP, 5-step)

### Step 1: Define the subproblem

- **What it's asking:** for prefixes of both strings, what is the LCS length?
- **Why this works:** if you can solve every prefix-pair subproblem, you can solve the full problem.
- **What the result tells us:** `LCS(i, j)` = length of the LCS of `A[0..i]` and `B[0..j]`.
- **Gotcha:** students often define the subproblem to be "LCS ending at i, j" — that is a different (harder) problem and the recurrence is uglier.

### Step 2: Write the recurrence

- **What it's asking:** how does `LCS(i, j)` relate to `LCS(i-1, j-1)`, `LCS(i-1, j)`, `LCS(i, j-1)`?
- **Why this works:** the optimal-substructure property says the full solution is composed of optimal subproblem solutions.
- **What the result tells us:** if `A[i] == B[j]` → `LCS(i, j) = 1 + LCS(i-1, j-1)`; else `LCS(i, j) = max(LCS(i-1, j), LCS(i, j-1))`.
- **Gotcha:** students forget the "else" branch and only handle the matching case.

### Step 3: Fill order and base case

- **What it's asking:** in what order do you fill the table so every dependency is already computed?
- **Why this works:** DP requires bottom-up evaluation (or memoization with top-down).
- **What the result tells us:** fill row by row, left to right. Base case: `LCS(0, *) = LCS(*, 0) = 0`.
- **Gotcha:** students often forget the base case row/column (zero-length prefix).

### Step 4: Traceback for the actual subsequence

- **What it's asking:** how do you recover the subsequence (not just its length)?
- **Why this works:** the DP table encodes the decisions; traceback reads them in reverse.
- **What the result tells us:** start at `LCS(n, m)`; at each cell, move to the predecessor that produced the value; collect matched characters.
- **Gotcha:** students often try to extract the subsequence from the LCS values directly without traceback, which fails.

### Step 5: Complexity + variation

- **What it's asking:** what is the time / space complexity, and what variations exist?
- **Why this works:** complexity analysis reveals when the algorithm fits the problem size.
- **What the result tells us:** O(nm) time, O(nm) space; rolling-array trick brings space to O(min(n, m)).
- **Gotcha:** students often state O(nm) space and forget the rolling-array optimization exists.

## When to deviate from the template

- **Single-line trivial computation:** skip the template; one line is enough.
- **Multi-path problem with intended comparison:** add an "Alternate path" section after the main walkthrough.
- **Open-ended research problem with no canonical solution:** the four-part template does not fit — recommend a different format (literature walk, design-doc walkthrough).
