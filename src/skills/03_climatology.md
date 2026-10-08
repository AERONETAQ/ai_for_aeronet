WHEN: "typical", "average", "seasonal cycle", "monthly/annual mean", "how much AOD at site X".
1. Aggregate daily -> monthly means only when the month has enough days; default rule: >= 5 daily values per
   calendar month, and an annual mean needs >= 9 valid months. State the rule you used and how many months/years
   it removed.
2. AOD is right-skewed (roughly log-normal): report mean AND median (and the 10th/90th percentiles when
   describing variability). Use the mean for comparison with satellite/model climatologies, the median for
   "typical day". Ångström exponent is roughly symmetric; the mean is fine.
3. Seasonal cycle = group by calendar month across all years (multi-year monthly climatology); show N years per
   month. Seasons, when asked: DJF, MAM, JJA, SON by calendar month, December counted with the following
   January and February, and say so; a southern-hemisphere site keeps the same labels (DJF = austral summer). Standard deviation across years = interannual variability; std of daily values within the month = day-to-day
   variability. Say which one you plotted.
4. Multi-year climatologies over a changing record are biased if some years are missing whole seasons: check that
   each month-of-year is represented by a similar number of years, otherwise say so.
   The same rules hold for the other tables, with their own units of sampling: inversion products from days with
   a retrieval (N_ > 0; absorption products only exist at AOD(440) >= 0.4, inversions skill), lunar statistics
   from nights (>= 5 nights per month, lunar skill), Level 1.5 only where Level 2.0 has nothing (data_levels skill).
5. A regional or multi-site mean is the mean of the site means (every site counts once), never the mean of all
   pooled days (a long record would dominate); give N sites and the spread across sites.
6. Figure, when the figures skill says one is warranted (a seasonal cycle asked to be shown usually is): line or
   bar of the 12 monthly values with error bars (std or IQR), y-axis label "AOD 500 nm", title with site name and
   the plotted period, N per month written on the points. Made last, from the checked table.
