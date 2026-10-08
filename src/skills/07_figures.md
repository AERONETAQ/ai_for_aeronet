WHEN: before any fig.savefig. A figure is the last step of a question, never the first. A saved figure is not a
checked figure: it belongs to the answer only after the figure check of step 5 says PASS.
1. Make one only when it earns its place: the question asks to show, plot or visualise; the result is a series or a
   distribution too long to read as numbers (a seasonal cycle, a time series, anomalies with their fit, an AOD–AE
   scatter, several sites side by side, a spatial pattern across sites: a map, maps skill); or a skill step names
   one as a check. A single number, a short ranking, a lookup or a "what do we have so far" question gets a table
   and no figure. A CSV you save that holds such a series is worth a figure; a CSV of a few rows is not.
2. Draw it from checked numbers only: self_check steps 1–3 come first; the figure is then plotted from the table
   you have already verified and saved. Never plot to explore; explore with print().
3. Last and once: all figures of a question in the last run_python call before the answer, one figure with panels
   rather than several files, saved once under a descriptive name. Every image costs about 2000 tokens on every
   later model call of this question, so: no early figures, no re-saves for cosmetics, no view_figure on a figure
   made in this question.
4. Self-explanatory: a scientist must understand the figure from the image alone, without the answer text.
   Everything drawn is explained inside the figure, in plain words:
   - title: site, quantity with wavelength, and the period actually plotted (not the record span);
   - every axis of every panel: quantity and unit ("AOD at 500 nm (unitless)"); dates on the x-axis of a time series;
   - a legend entry for every line, marker, colour, band, error bar and reference line, saying what it is and how
     it was computed ("monthly mean ± 1 SD across years", "linear fit, −0.012 per decade"); a colour bar has a
     label with unit;
   - every annotation and abbreviation defined in the figure ("n = years per month", DJF = Dec–Feb);
   - the data in one small line: "AERONET Level 2.0 daily means, Version 3";
   - no raw column or variable names (AOD_500nm, clim, sd) and no default labels anywhere.
   Honest drawing: when the number of years or days behind the points varies, write n on each point or as a
   second row of tick labels; a point from n = 1 gets no error bar and a distinct marker, named in the legend;
   missing months or years are gaps (NaN), never zeros; the same y-axis for sites compared; log y when AOD spans
   decades. Text readable and not overlapping; figsize at most 10x6 in, dpi 110.
5. Figure check, mandatory, straight after the image comes back in the run_python result. Look at the image
   itself and read from its axes, not from the table:
   - every panel: the highest and the lowest point, its value (≈) and where it sits (month, year, site);
   - title period, axis labels with units, legend entries against the lines drawn, the n labels;
   - nothing empty, flat, cut off, overlapping or unreadable, and no spike the table does not have;
   - step 4 holds: anything drawn that the figure itself does not explain (a line, marker, colour, bar,
     abbreviation, n) is a FAIL, not a cosmetic.
   Compare each with the checked table. Your next message then starts with this note, one per figure:
   "Figure check <file>: <panel> max ≈<value> at <where>, min ≈<value> at <where> (table: <value>, <value>);
   <next panel> ...; title period, labels, legend, n OK; every element explained in the figure -> PASS", or "... -> FAIL: <what is wrong>".
   PASS: the note stands before final_result. FAIL: correct the code, save again under the same name, and check
   the new image the same way. Never answer on a FAIL and never explain one away. After two failed redraws,
   answer without the figure and say why.
