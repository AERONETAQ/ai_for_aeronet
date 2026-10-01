WHEN: before any fig.savefig. A figure is the last step of a question, never the first.
1. Make one only when it earns its place: the question asks to show, plot or visualise; the result is a series or a
   distribution too long to read as numbers (a seasonal cycle, a time series, anomalies with their fit, an AOD–AE
   scatter, several sites side by side); or a skill step names one as a check. A single number, a short ranking,
   a lookup or a "what do we have so far" question gets a table and no figure. A CSV you save that holds such a
   series is worth a figure; a CSV of a few rows is not.
2. Draw it from checked numbers only: self_check steps 1–3 come first; the figure is then plotted from the table
   you have already verified and saved. Never plot to explore; explore with print().
3. Last and once: all figures of a question in the last run_python call before the answer, one figure with panels
   rather than several files, saved once under a descriptive name. Every image costs about 2000 tokens on every
   later model call of this question, so: no early figures, no re-saves for cosmetics, no view_figure on a figure
   made in this question.
4. Content: title = site, variable and the period that is actually plotted (not the record span); axis labels with
   units; legend entries = the series drawn; when the number of years or days behind the points varies, write n
   on each point or as a second row of tick labels; a point from n = 1 gets no error bar and a distinct marker;
   missing months or years are gaps (NaN), never zeros; the same y-axis for sites compared; log y when AOD spans
   decades; dates on the x-axis of a time series. figsize at most 10x6 in, dpi 110.
5. The image comes back in that run_python result: read it back (self_check step 4) before you answer.
