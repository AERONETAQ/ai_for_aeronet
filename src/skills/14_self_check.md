WHEN: always. Order: numbers (steps 1–3) -> figure, if one is warranted (figures skill) -> figure check (4) ->
answer (5–6). Say in one line at the end what you checked.
1. Evidence: every number, date, N and file name in the answer must appear in a tool result of this question.
   Nothing from memory, nothing rounded from a guess.
2. Independent check: recompute the headline result by a second route and compare. [examples: an annual mean
   from the daily rows instead of from the monthly table; a count from .notna().sum() instead of len(); a slope
   from a sub-period; a total from a different groupby; a per-site number from a DuckDB aggregation recomputed in
   pandas from that one site's rows; a monthly mean from AERONET's monthly table against your own from the
   daily rows]. If the two differ beyond rounding, find out why.
3. Plausibility: values inside their physical range [AOD 0–5 (lunar AOD down to −0.02 on clean nights), Ångström
   exponent −0.5–3, water 0–8 cm, SSA 0.6–1, absorption AOD 0–0.5, real refractive index 1.33–1.6, imaginary
   0.0005–0.5, depolarization ratio 0–0.5, dV/dln r >= 0 with fine-mode median radius 0.05–0.5 µm and coarse 1–10 µm,
   sphericity 0–100 %, sky residual of a kept retrieval <= 8 %, solar zenith angle of a Level 2.0 almucantar
   >= 50°, local hour 0–24, lunar phase angle −100–100°, air mass 1–7]; dates inside the site's record; N consistent from step to step;
   no silent NaN drop (compare rows before and after filters and before and after every join of two tables);
   lunar counts after drop_duplicates; monthly tables counted without their empty months; one level, one scan
   type and one filter set per statistic; Level 1.5 inversions screened before any absorption number; memory
   after the last cell well under the limit (a turn that needed the release lines says so); a result that looks too clean
   or too extreme deserves one more look.
4. Figure check: for every PNG saved, exactly as the figures skill step 5 says: read the image, compare it
   with the checked table, write the "Figure check <file>: ... -> PASS" or "-> FAIL: ..." note. A spike that
   is a fill value or a wrong join rather than an event is a FAIL.
5. Mismatch: fix it, do not explain it away. Rerun the step, then re-check. Only answer when the checks agree.
6. Report: one "Checked:" line at the end of the answer naming each check and, for each figure, what you read off
   it and that it matched, e.g. "Checked: annual means recomputed from daily rows (match to 3 decimals); N per
   year consistent; figure gsfc_annual_aod500.png read back: max 0.142 in 2003, min 0.061 in 1998, both equal the
   table; title period 1997–2025 = data period; n per year on the points."
