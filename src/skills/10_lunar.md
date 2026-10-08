WHEN: "night", "night-time", "lunar", "moon", "day–night difference", "diurnal cycle" beyond daylight, "polar
night", "after sunset", "24-hour coverage". Table: DATA_LUNAR (all points: one row per measurement).
1. What it is: the Model-T Cimel measures the direct lunar irradiance at 440, 500, 675, 870, 1020 and 1640 nm
   (no UV: the Moon is too faint). AOD follows from the ROLO lunar-irradiance model with AERONET's empirical
   phase-angle correction, derived from solar/lunar Langley pairs at Mauna Loa and Izaña (the correction is often
   about 10 %). Level 2.0 lunar AOD was released in June 2025 (Schafer et al. 2026): at sites with more than a
   decade of data the mean day–night difference is within ±0.01 at 440 nm and smaller at longer wavelengths;
   in 3-hour day–night transition windows under stable low AOD the differences in AOD, Ångström exponent and
   water vapour are statistically negligible. Nominal uncertainty about 0.01–0.02 (Barreto et al. 2016), larger
   at large phase angle and large air mass, where the triplet variability grows.
2. Sampling is unlike the solar record: measurements exist only with the lunar phase angle within about ±90°
   (the bright half of each cycle: about 12–14 nights a month, none around new Moon) and the Sun more than 8°
   below the horizon; the usable night is longest around full Moon and changes by hours within a week; at high
   latitude the summer has almost no lunar data and the polar night only lunar data. A monthly night statistic
   needs enough nights (default >= 5 nights with >= 5 measurements each; state the rule) and the answer says
   which part of the lunar cycle and which hours were sampled. A night and a day are never compared without
   this caveat.
3. From points to nights: a night spans two UTC dates. Assign each measurement to the local night it belongs to:
   night = (datetime_utc + longitude / 15 hours − 12 hours).date, the local calendar date on which that night
   began. Then nightly mean, median, N and the phase-angle range per night; a night with N < 5 is a weak
   estimate. Drop AERONET's verbatim duplicate rows first (drop_duplicates on site + datetime_utc).
4. Day against night with this corpus: the solar tables hold daily means only, so pair each night with the solar
   daily mean (DATA, Level 2.0) of the day it began (and of the following day when the question is about the
   morning side), on days that have both; report N pairs, the mean and median night-minus-day difference, its
   sign and spread, per wavelength, and when a significance is asked the Wilcoxon signed-rank test on the paired
   differences. The fairest pairs are stable days (the two bracketing daily means agree within 0.05); a mean
   difference within ±0.01 is inside the measurement uncertainty, not a diurnal cycle, however small its
   p-value. Within one night the evening and morning halves (before and after local midnight) can be compared
   from the points themselves. The 3-hour transition-window test of Schafer et al. needs solar all-points data,
   which this corpus does not have: say so when asked for it. Trends of night-time AOD are not warranted: the
   record starts in 2015 and its sampling follows the lunar cycle; describe by year with N nights instead.
5. Known biases to state: hazy nights are lost first at 440 nm (the faint Moon sets a maximum measurable AOD 2–3
   times lower than by day; on average 3 % of lunar 440 nm points are removed against 0.3 % at 675 and 870 nm,
   more than 8 % at hazy sites), so night statistics at polluted or dusty sites are biased low at 440 nm:
   compare day and night at 500 or 675 nm there and report how many nights have 440 nm. No sky scans at night
   means no aureole (curvature) cirrus check: slightly more thin-cirrus contamination and a lowered Ångström
   exponent in some seasons (monsoon south-east Asia, the ITCZ). No inversions at night. AOD slightly below
   zero on very clean nights is measurement noise within ±0.01: keep it, do not clip, and say so.
6. Columns to use: AOD_<λ>nm, Angstrom_Exponent_440_870nm (the 380_500 column has no 380 nm channel at night:
   avoid it), Precipitable_Water_cm, Lunar_Phase_Angle_Degrees (0 = full Moon, negative = waxing, positive =
   waning), Optical_Air_Mass (report its range; noise and the faint-signal loss grow with it, so a comparison
   can be restricted to air mass <= 3 with the restriction stated), Lunar_Zenith_Angle_Degrees,
   Triplet_Variability_<λ> as a noise indicator (a convention of this skill, not AERONET's: report, or screen,
   nights whose median triplet variability exceeds 0.02). Read columns and sites selectively: the table has
   8 million rows.
7. Figures, when warranted: the nightly means as a time series with the solar daily means of the same site
   overlaid in a distinct marker and colour, the same y-axis; a histogram or box plot of night-minus-day
   differences; the phase angle as marker colour when the question is about the lunar cycle; a map of sites
   coloured by the mean night-minus-day difference uses a diverging colour map centred on zero (maps skill).
   Titles and legends name "lunar Level 2.0, all points" and "solar Level 2.0, daily means".
