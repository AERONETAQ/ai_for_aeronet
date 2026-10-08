WHEN: "event", "episode", "extreme days", "dust storm", "smoke", "when was AOD highest".
1. "High" must be relative to the site's own climatology: flag a day when AOD 500 nm exceeds the site's
   multi-year 95th percentile for that calendar month (default), or a fixed value the user gives. State the
   threshold.
2. Group consecutive flagged days into episodes; report start, end, duration, peak AOD and its date, mean AE
   during the episode (for the likely aerosol type, see the aerosol_type skill), and N days.
3. Rank episodes by peak or by cumulative AOD above the threshold; list the top 10 as a table.
4. Figure, when warranted (a "when did it happen" question usually is): the daily series for the year(s) of
   interest with the threshold line and the episodes shaded; the table of episodes is always reported.
5. A missing day inside an episode is likely cloud (no Level 2.0 data), not a gap in the event; say so rather than
   splitting the episode, unless the gap is > 2 days.
6. Do not name the source (a specific fire, storm) — the data cannot show it; describe timing, magnitude and type.
7. The other tables add to an episode: the lunar nights inside it (did the plume persist after sunset: lunar
   skill), the inversion days inside it (how absorbing, how fine: inversions skill), and the Level 1.5 days when
   the episode is too recent for Level 2.0 (data_levels skill). The daily maximum of an extreme day is biased
   low by the faint-signal limit (aod_measurement skill step 4): say so for peaks above about 2.
