WHEN: the first step of every analysis, before any statistic.
1. Which table answers the question: solar AOD, climatology, trend, episode, site comparison -> DATA (Level 2.0,
   the reference); the recent months, "latest", a site or period missing from Level 2.0 -> DATA_L15 with the
   data_levels skill; absorption, size, shape, refractive index, forcing -> DATA_INV with the inversions skill;
   night, lunar, day–night -> DATA_LUNAR with the lunar skill; water vapour -> the water_vapour skill (solar daily
   tables and lunar). A cross-table question joins on AERONET_Site_Name
   + date (lunar: on the night, lunar skill step 3) and names each table and its level in the answer.
2. list_sites(name_contains=...) gives the exact site name (case-sensitive, underscores: "Mauna_Loa"), coordinates
   and record span in one table (dataset=); site_coverage(site) gives the spans in all four tables at once;
   describe_columns(site, dataset=...) shows which wavelengths or products that site has and on how many days:
   one call, for the site the analysis is about. A place name that is not a site goes through geocode, then
   nearest_sites(lat, lon, max_km); a country or state through the Natural Earth borders (maps skill).
   For a question over many sites (a region, a threshold) do not call these per site: load the few columns you
   need in run_python and count there. Then load only the columns you need, filtered by site, e.g.
   pd.read_parquet(DATA, columns=["AERONET_Site_Name","date","year","month","AOD_500nm","N_AOD_500nm"],
                   filters=[("AERONET_Site_Name","==","GSFC")])
3. Describe the record before using it: days (nights, retrieval days) per year, gaps, and the coverage of the
   wavelength or product you chose (every column is NaN where it was not measured or failed that level's
   screening). Coverage is uneven: instruments are moved, break, and are recalibrated; gaps are normal, not
   errors. The four records of one site have different spans: Level 2.0 ends months to two years before
   Level 1.5 (site by site), the inversions start in 2014 and hold far fewer days, the lunar record starts in
   2015 and covers half of each month.
4. One row = one day in the three daily tables (the mean of that day's measurements or retrievals, stamped 12:00
   UTC; N_<col> is how many went in; a day with N=1 is a real but weak estimate — say so if it matters) and one
   measurement in the lunar table (nights are built from it, lunar skill).
5. Level 2.0 = cloud-screened AND quality-assured with final calibration (Version 3, Giles et al. 2019). You do not
   need extra cloud screening. Do not "clean" outliers: high AOD days are real events (dust, smoke). What the
   number itself means, its accuracy and its clear-sky sampling: aod_measurement skill.
6. Wavelengths: 500 nm is the standard reporting wavelength; 440/675/870/1020 nm are on every instrument;
   340/380 nm and 1640 nm only on some, never at night. AOD_531nm and AOD_551nm etc. are rarely populated; the
   inversion products come at 440/675/870/1020 or 443/667/865/1020 nm. Check before use.
7. Keep memory small: never load all columns for all sites at once (the daily tables are ~1 GB each, the lunar
   table 8 million rows, the inversion table 337 columns); aggregate per site, then combine.
8. A variable listed in the state block is reused, not reloaded, but first a one-line cell prints its shape and
   columns: an earlier turn loaded only the columns it needed, so the wavelength or Ångström column you want may
   not be in it. If it is missing, load a new frame with the columns you need instead of patching the old one.
