WHEN: "trend", "is AOD increasing/decreasing", "change over years", "long-term".
1. Requirements: >= 8 years of data with >= 9 valid months each; otherwise say the record is too short and stop at
   a description. Check for large gaps or an instrument change (AERONET_Instrument_Number) that splits the record.
2. Remove the seasonal cycle first: monthly means (>= 5 days; from the daily table, or AERONET's own from
   DATA_MONTHLY with NUM_DAYS_<column> >= 5, which is the route for trends at many sites: say which, they
   differ slightly because AERONET's leave out days with fewer than 3 measurements) -> monthly anomalies =
   value minus the multi-year mean of that calendar month. Fit the trend to the anomaly time series with time in decimal years, NaN months
   dropped.
3. Use the Theil–Sen slope with the Mann–Kendall test (robust to the skewed distribution and outliers):
     from scipy import stats
     slope, intercept, lo, hi = stats.theilslopes(y, t, alpha=0.95)     # slope + 95 % confidence interval
     tau, p = stats.kendalltau(t, y)                                     # Mann–Kendall on a time series
   Cross-check with OLS that allows for autocorrelated residuals:
     import statsmodels.api as sm
     ols = sm.OLS(y, sm.add_constant(t)).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
   Report the OLS slope and its HAC p-value next to the Theil–Sen result; if they disagree on significance, say so.
4. Report: slope in AOD per year AND in % per year relative to the record mean, the confidence interval, n months
   used, p-value, the period. "Significant" = p < 0.05, and say so explicitly either way.
5. Caveats to state: monthly anomalies are autocorrelated (the Kendall p is optimistic, the HAC p is the honest
   one); a trend can be driven by the first or last years — the anomalies with the fitted line are the one figure
   a trend question always warrants: make it last and look;
   attribution (emissions, dust, fires) is outside the data — do not claim causes.
6. Trends are Level 2.0 only (data_levels skill). Trends of inversion products follow the inversions skill
   step 6 (almucantar record only, the AOD(440) >= 0.4 selection stated); lunar AOD has no trend (lunar skill).
   Trends at many sites: the monthly means of all sites come from one DuckDB aggregation, the fit runs per
   site on that small table, and the answer gives the number of sites that met step 1 and how many are
   significant with each sign; with many sites tested, about 5 % reach p < 0.05 by chance: say so.
