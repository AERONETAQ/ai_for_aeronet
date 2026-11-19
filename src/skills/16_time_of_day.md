WHEN: "diurnal", "time of day", "morning against afternoon", "hourly", "within the day", "at what time", a single
retrieval or measurement rather than a daily mean, or daily means that you compute yourself from points.
Tables with a time of day: DATA_ALM and DATA_ALM_L15 (almucantar retrievals by day), DATA_LUNAR and
DATA_LUNAR_L15 (AOD measurements by night). Solar AOD and the hybrid inversions exist here only as daily and
monthly means: a daytime AOD diurnal cycle cannot be computed from this corpus; say so instead of
approximating it.
1. Time: datetime_utc is UTC. Time-of-day statistics use the local solar time, UTC + longitude / 15 hours
   (large_tables skill step 6 has the expression); the civil time zone that geocode returns is used only when
   the user asks for clock time. Say which one the answer uses.
2. AERONET's day is the site's local day, not the UTC day. A daily mean is the arithmetic mean of every
   retrieval whose local solar date (datetime_utc + longitude / 15 h) is that day: AERONET's daily inversion
   tables follow this rule. At sites far from Greenwich (Hawaii, east Asia, Australia, the Pacific) the UTC
   date splits one day's retrievals over two dates. So daily means made from DATA_ALM (Level 2.0 has no daily
   table) are grouped by the local day, with N retrievals per day kept, and only then follow the climatology
   rules. A retrieval day typically holds 2 to 5 almucantar retrievals.
3. The almucantar samples the day unevenly, by design. Level 2.0 needs a solar zenith angle of at least 50° at
   the scan (Level 1.5 reaches lower Sun angles), because a low Sun gives the scan its wide range of scattering
   angles. Retrievals therefore sit in the morning and the afternoon and reach local noon only when the noon
   Sun is low: in winter at middle and high latitudes, never in the tropics, and not in mid-latitude summer.
   Hour of day and season are confounded: a mean by local hour over a whole record mixes winter noons with
   summer mornings and shows a "diurnal cycle" that is a seasonal one. Any time-of-day statistic is therefore computed inside one season or month, shows N per hour bin, and
   leaves bins with fewer than 30 retrievals uninterpreted (a convention of this skill: state it).
4. The honest test of a within-day change is paired: for each local day with retrievals both before and after
   local noon, the afternoon mean minus the morning mean; report N days, the median difference and, when a
   significance is asked, the Wilcoxon signed-rank test. Always give the same paired difference for the AOD of
   the retrievals (Coincident_AOD440nm): absorption and size change with the aerosol load, so a change in SSA
   that comes with a change in AOD is a change of air mass or loading, not a property of the hour. A difference
   inside the retrieval uncertainty (SSA 0.03, fine radius 0.01 µm, AOD 0.01) is "no detectable change",
   whatever its p-value. The geometry itself changes with the hour (the scattering-angle range grows with the
   solar zenith angle), so small systematic morning–noon differences can be retrieval effects.
5. Absorption by hour describes hazy hours only: SSA, refractive index, absorption AOD, lidar and depolarization
   ratios exist in Level 2.0 only at AOD(440) >= 0.4 (inversions skill). Size distribution, volume and radii
   exist at any AOD and suit time-of-day work better.
6. Single events: the points put a retrieval at its time. For an episode (episodes skill) list the retrievals
   of its days with local time, Coincident_AOD440nm, the Ångström exponent, SSA and fine fraction, and read the
   sequence; one retrieval is one sky scan of a few minutes, with the uncertainty of a single retrieval, not of
   a mean.
7. Nights: the lunar tables hold every measurement; nights, evening and morning halves and the pairing with the
   solar daily means follow the lunar skill. Night-time sampling has its own confounder, the lunar cycle, as
   daytime retrievals have the solar zenith angle.
8. Figures, when warranted: local solar hour on the x-axis, one line or panel per season, N written per bin,
   the uncertainty band of the quantity drawn (SSA ±0.03); for a morning–afternoon test a histogram of the
   paired differences with zero marked. The caption names the scan type, the level and the solar-zenith-angle
   limit.
