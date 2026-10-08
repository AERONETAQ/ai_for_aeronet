WHEN: "water vapour", "precipitable water", "humidity", "PW", "column water", "moist / dry season", or AOD
against water vapour. Columns: Precipitable_Water_cm in the solar daily tables and the lunar table (with
Triplet_Variability_Precipitable_Water_cm at night); not in the inversion table.
1. What it is: total column water vapour from the 935 nm absorption band, in cm of liquid water (1 cm = 1 g/cm²
   = 10 kg/m²), retrieved only when the direct Sun (or Moon) is cloud-free, so its sampling is the AOD's. Typical
   values 0.1–0.5 cm at polar and high mountain sites, 1–3 cm mid-latitude, 4–6 cm in the humid tropics; the
   physical range is 0–8 cm. Uncertainty about 10 % (Smirnov et al. 2004; Pérez-Ramírez et al. 2014), with a
   dry bias of a few percent against radiosondes and GPS in Version 2 that Version 3 reduced (Giles et al. 2019).
   Daily means, N counts and the Level 1.5 / 2.0 rules are the AOD's (data_access, data_levels skills).
2. Analyse it like AOD but without the log: the seasonal cycle, trends and site comparisons follow the
   climatology, trend and site_comparison skills (mean and median both fine; the distribution is mildly skewed).
   Night values from the lunar table follow the lunar skill (nights, not days; phase-angle sampling).
3. AOD against water vapour: a positive correlation in summer or monsoon months usually reflects humid air masses
   and hygroscopic growth of the fine mode, not more particles; report the correlation per season with N, never
   as a cause. The Ångström exponent drops when particles swell: say so when AE and PW move together.
4. Water vapour is not an aerosol: never mix it into AOD statistics, keep its own axis and unit (cm) in every
   figure, and name the channel ("precipitable water from the 935 nm band") in the legend.
