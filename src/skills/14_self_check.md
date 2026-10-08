WHEN: always. Order: numbers (steps 1–3) -> figure, if one is warranted (figures skill) -> figure check (4) ->
answer (5–6). Say in one line at the end what you checked.
1. Evidence: every number, date, N and file name in the answer must appear in a tool result of this question.
   Nothing from memory, nothing rounded from a guess.
2. Independent check: recompute the headline result by a second route and compare. [examples: an annual mean
   from the daily rows instead of from the monthly table; a count from .notna().sum() instead of len(); a slope
   from a sub-period; a total from a different groupby]. If the two differ beyond rounding, find out why.
3. Plausibility: values inside their physical range [AOD 0–5 (lunar AOD down to −0.02 on clean nights), Ångström
   exponent −0.5–3, water 0–8 cm, SSA 0.6–1, absorption AOD 0–0.5, real refractive index 1.33–1.6, imaginary
   0.0005–0.5, depolarization ratio 0–0.5, dV/dln r >= 0 with fine-mode median radius 0.05–0.5 µm and coarse 1–10 µm,
   lunar phase angle −100–100°, air mass 1–7]; dates inside the site's record; N consistent from step to step;
   no silent NaN drop (compare rows before and after filters and before and after every join of two tables);
   lunar counts after drop_duplicates; one level and one filter set per statistic; a result that looks too clean
   or too extreme deserves one more look.
4. Figure check (figures skill step 5): every PNG you save is shown to you in the run_python result. Read it like
   a reviewer, from the image and not from the table: for each panel the highest and the lowest value and where
   they sit, the title period, the axis labels, the legend against the lines drawn, the n labels, and that everything drawn is explained inside the figure. They must agree
   with the checked table; no empty, flat or all-NaN panel; no spike that is a fill value or a wrong join rather
   than an event. Write the "Figure check <file>: ... -> PASS" or "-> FAIL: ..." note as your next message. A
   figure that fails is corrected, saved again under the same name and checked again, not explained away.
5. Mismatch: fix it, do not explain it away. Rerun the step, then re-check. Only answer when the checks agree.
6. Report: one "Checked:" line at the end of the answer naming each check and, for each figure, what you read off
   it and that it matched, e.g. "Checked: annual means recomputed from daily rows (match to 3 decimals); N per
   year consistent; figure gsfc_annual_aod500.png read back: max 0.142 in 2003, min 0.061 in 1998, both equal the
   table; title period 1997–2025 = data period; n per year on the points."
