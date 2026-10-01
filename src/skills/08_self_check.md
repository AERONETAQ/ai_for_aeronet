WHEN: always. Order: numbers (steps 1–3) -> figure, if one is warranted (figures skill) -> figure read-back (4) ->
answer (5–6). Say in one line at the end what you checked.
1. Evidence: every number, date, N and file name in the answer must appear in a tool result of this question.
   Nothing from memory, nothing rounded from a guess.
2. Independent check: recompute the headline result by a second route and compare. [examples: an annual mean
   from the daily rows instead of from the monthly table; a count from .notna().sum() instead of len(); a slope
   from a sub-period; a total from a different groupby]. If the two differ beyond rounding, find out why.
3. Plausibility: values inside their physical range [AOD 0–5, Ångström exponent −0.5–3, water 0–8 cm]; dates inside
   the site's record; N consistent from step to step; no silent NaN drop (compare rows before and after filters);
   a result that looks too clean or too extreme deserves one more look.
4. Figure read-back: every PNG you save is shown to you in the run_python result. Read it like a reviewer and write
   down what you see: for each panel the title, the axis labels, the highest and the lowest value you can read off
   and where they sit (which month, year or site), the number of series and the legend entries. Then compare with
   the checked table: the max and min and their positions must agree; the title period must be the period in the
   data; n must be visible where it varies; no empty, flat or all-NaN panel; no spike that is a fill value or a
   wrong join rather than an event; the legend must match the lines drawn. A figure that fails is fixed and saved
   again under the same name (the corrected image is shown to you again), not explained away.
5. Mismatch: fix it, do not explain it away. Rerun the step, then re-check. Only answer when the checks agree.
6. Report: one "Checked:" line at the end of the answer naming each check and, for each figure, what you read off
   it and that it matched, e.g. "Checked: annual means recomputed from daily rows (match to 3 decimals); N per
   year consistent; figure gsfc_annual_aod500.png read back: max 0.142 in 2003, min 0.061 in 1998, both equal the
   table; title period 1997–2025 = data period; n per year on the points."
