WHEN: "latest", "recent", "this year", "near-real-time", "provisional", "Level 1.5", a period after the Level 2.0
record of the site ends, a site that is not in Level 2.0, or any comparison of the two levels.
1. Level 2.0 (DATA) is the reference: cloud-screened, quality-assured, pre- AND post-field calibration applied
   (Giles et al. 2019). AOD uncertainty about 0.01 at 400 nm and longer, 0.02 in the UV (340, 380 nm). Use it
   for climatologies, trends, episodes and anything to be published. Its record ends when the instrument's last
   post-field calibration was applied: a few months to two years before today, on a different date at every
   site (GSFC January 2026, Kanpur November 2025 at the time of writing). Report that end date whenever
   "recent" or "latest" is asked.
2. Level 1.5 (DATA_L15) is the near-real-time product: the same automatic cloud screening and instrument checks,
   but the pre-field calibration only, so it is provisional and the values change when the final calibration
   arrives. The pre-field-only AOD is biased high relative to the final value: about +0.003 to +0.009 soon after
   calibration, +0.010 to +0.017 after about 1.5 years in the field, up to about +0.02 (one sigma about 0.02)
   (Giles et al. 2019, Sect. 4). It also holds instruments that never get a final calibration (lost, damaged,
   not the site's primary instrument) and days that the Level 2.0 quality checks removed.
3. One level per statistic. Never pool Level 1.5 and Level 2.0 rows in one mean, series or trend. When a question
   spans both the Level 2.0 period and the months only Level 1.5 has, compute the two parts separately, label
   them, and say where the Level 2.0 record ends. A trend or climatology is Level 2.0 only; "the last month"
   is Level 1.5 and the answer says "provisional (Level 1.5)".
4. Comparing the levels (how much of Level 1.5 reaches Level 2.0, how large the calibration correction was):
   inner join on AERONET_Site_Name + date; report N common days, the fraction of Level 1.5 days present in
   Level 2.0 within the Level 2.0 period, and per wavelength the mean and median of Level 1.5 minus Level 2.0 with
   its sign. Differences within ±0.02 are the expected calibration adjustment; larger ones point to a degrading
   filter or a changed instrument (compare AERONET_Instrument_Number). A Level 1.5 day missing from Level 2.0
   inside the Level 2.0 period was removed by the Level 2.0 checks or came from a non-primary instrument; it is
   not a gap in the Level 1.5 record.
5. A site only in Level 1.5 (1,613 sites against 1,485) has no finally calibrated data at all: say so, and treat
   every number from it as provisional.
6. Both tables are daily means of the same kind (12:00 UTC stamps, N_ counts): the same climatology, episode and
   comparison skills apply, with the level named in every table, figure title and the answer.
