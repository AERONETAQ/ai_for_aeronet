WHEN: always, before interpreting any AOD number; and whenever the question asks what AOD "means", compares AOD
with surface air quality, satellites or models, or asks about extreme values, detection limits or clouds.
1. What is measured: a Cimel sun photometer points at the Sun (the Moon at night) and measures the direct beam in
   narrow bands; AOD follows from the Beer–Lambert law, AOD = ln(V0/V) / m − (Rayleigh + gas optical depths),
   with V0 the top-of-atmosphere signal from Langley calibration at Mauna Loa or Izaña and m the optical air
   mass (1 at zenith, measurements up to 7). Rayleigh scattering (pressure-scaled to the site elevation), ozone
   and NO2 are removed, water vapour for the 935 nm band, so AOD is the aerosol-only, column-integrated
   extinction, unitless, of everything between the instrument and the top of the atmosphere.
2. Sampling: a triplet of 3 measurements over 1 minute, every 15 minutes by day (more often at high air mass
   for the Langley schedule), about every 3 minutes by night. A daily mean is the arithmetic mean of every
   triplet of that UTC day that passed the level's screening (N_<column>); it is not weighted by time of day,
   so a day with morning data only is a morning mean: N tells the weight of a day.
3. Clear-sky bias: AOD exists only when the direct beam is cloud-free, so every AERONET statistic describes
   cloud-free daytime (or moonlit night-time) conditions: humid, cloudy seasons are under-sampled, days per
   month vary, and comparisons with satellite or model climatologies must say "clear-sky, daytime, cloud-free
   sampling". The cloud screening (Giles et al. 2019: triplet variability above 0.01 or 0.015 × AOD, time-series
   smoothness, Ångström exponent and 3-sigma checks, the aureole curvature check for thin cirrus) is already
   applied: do not screen again, and never remove high values as outliers.
4. Magnitudes (500 nm): 0.01–0.05 at Mauna Loa and polar sites, 0.05–0.15 clean marine and remote continental,
   0.1–0.3 rural and clean urban, 0.3–0.6 polluted cities and the Indo-Gangetic Plain in winter, 0.5–2 in dust
   outbreaks and biomass-burning seasons, above 2 only in extreme smoke or dust. The faint-signal limit
   Vmin = V0/1500 caps the measurable total optical depth at about 7.3 for air mass 1 and about 1 at air mass 7,
   lower by 2–3 times at night, so the heaviest hours of an extreme event are missing from the record and the
   daily mean of such a day is biased low: say so when a maximum is reported.
5. Accuracy: 0.01 for wavelengths of 400 nm and longer, 0.02 in the UV (340, 380 nm) for field instruments
   with final calibration (Eck et al. 1999; Giles et al. 2019); Level 1.5 adds the pre-field calibration drift
   (data_levels skill). Two AODs that differ by less than 0.01–0.02 are the same; a difference between two
   long-term means can still be significant when N is large, but is only meaningful above the accuracy.
   The Ångström exponent is unreliable at low AOD (an error of 0.01 in AOD is a large fraction of 0.05):
   aerosol_type skill, AOD(440) >= 0.15 for typing. The 1640 nm channel (InGaAs detector) is on some
   instruments only and is temperature-sensitive; 340 and 380 nm have the largest uncertainty.
6. What AOD is not: not a surface concentration (PM2.5): aerosol aloft (transported dust or smoke above the
   boundary layer) raises AOD without touching the ground, and a shallow polluted layer can give a modest AOD;
   AERONET gives no vertical profile, no particle mass and no chemistry. The inversion products add size, shape
   and absorption of the column (inversions skill), the Ångström exponent the fine/coarse balance (aerosol_type
   skill). When a question asks about air quality or health, answer about the column and say this.
7. Spectral behaviour: AOD decreases with wavelength for fine particles (steeply: Ångström exponent 1.5–2.5),
   is nearly flat for coarse dust and sea salt (0–0.5); 500 nm is the conventional reporting wavelength, 550 nm
   the satellite one (interpolate with the Ångström law, aerosol_type skill, and say so). Wavelengths differ by
   instrument: check which exist at the site (describe_columns) before choosing, and never mix 440 with 443 nm
   or 870 with 865 nm as if they were the same channel.
