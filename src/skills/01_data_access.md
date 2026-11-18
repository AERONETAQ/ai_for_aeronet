WHEN: the first step of every analysis, before any statistic.
1. Which table answers the question (the data dictionary lists all 13; one level and one scan type per statistic):
   - solar AOD over many sites or many years, where a monthly mean is enough (climatology, trend, ranking, map)
     -> DATA_MONTHLY, AERONET's own monthly means, a small table; daily values, episodes, medians and
     percentiles, paired comparisons, a monthly rule of your own -> DATA (Level 2.0 daily means, the reference);
   - the recent months, "latest", a site or period missing from Level 2.0 -> DATA_L15 or DATA_L15_MONTHLY with the
     data_levels skill;
   - absorption, size, shape, refractive index, forcing -> the inversion tables with the inversions skill:
     DATA_ALM (almucantar scans, Level 2.0, every retrieval, 1993 →, the widest network) for long records and
     most sites; DATA_INV (hybrid scans, Level 2.0 daily means, 2014 →) for the Model-T instruments and for
     retrievals nearer noon; their monthly and Level 1.5 versions as that skill says;
   - night, lunar, day–night -> DATA_LUNAR (DATA_LUNAR_L15 for the recent months) with the lunar skill;
   - time of day, single retrievals or measurements -> the all-points tables with the time_of_day skill;
   - water vapour -> the water_vapour skill (solar tables and lunar).
   A cross-table question brings each table to a common unit first (site-day, site-night, site-month), joins on
   AERONET_Site_Name + date, and names each table, its level and its scan type in the answer.
2. list_sites(name_contains=...) gives the exact site name (case-sensitive, underscores: "Mauna_Loa"), coordinates
   and record span in one table (dataset=); site_coverage(site) gives the spans in all 13 tables at once;
   describe_columns(site, dataset=...) shows which wavelengths or products that site has and on how many days:
   one call, for the site the analysis is about. A place name that is not a site goes through geocode, then
   nearest_sites(lat, lon, max_km); a country or state through the Natural Earth borders (maps skill).
   For a question over many sites (a region, a threshold) do not call these per site: count in run_python.
   Then load only what the question needs, exactly as the large_tables skill says: one site = a column list and
   a site filter; many sites = one aggregation inside DuckDB that returns only the result.
3. Describe the record before using it: days (nights, retrievals, months) per year, gaps, and the coverage of the
   wavelength or product you chose (every column is empty where it was not measured or failed that level's
   screening). Coverage is uneven: instruments are moved, break, and are recalibrated; gaps are normal, not
   errors. The records of one site have different spans: Level 2.0 ends months to two years before Level 1.5
   (site by site); almucantar inversions start in 1993, hybrid ones in 2014, and both hold far fewer days than
   AOD; the lunar record starts in 2015 and covers half of each month; a monthly table has a row for every
   month of the site's span, most of them empty.
4. What one row is: one day in a daily table (the mean of that day's measurements or retrievals, stamped
   12:00; N_<col> is how many went in; a day with N=1 is a real but weak estimate — say so if it matters); one
   month in a monthly table (the mean of its daily means; NUM_DAYS_<col> and NUM_POINTS_<col> say how many days
   and measurements); one measurement or one retrieval in an all-points table (nights and days are built from
   them: lunar and time_of_day skills).
5. Level 2.0 = cloud-screened AND quality-assured with final calibration (Version 3, Giles et al. 2019): no extra
   cloud screening and no "cleaning" of outliers; what the number means, its accuracy and its clear-sky sampling
   are in the aod_measurement skill. Level 1.5 is not only "less calibrated": for inversions it is unscreened
   (data_levels and inversions skills).
6. Wavelengths: 500 nm is the standard reporting wavelength; 440/675/870/1020 nm are on nearly every instrument
   (the ocean-colour ones carry 443/667/865 instead);
   340/380 nm and 1640 nm only on some, never at night. AOD_531nm and AOD_551nm etc. are rarely populated; the
   inversion products come at 440/675/870/1020 or 443/667/865/1020 nm. Check before use.
7. A variable listed in the state block is reused, not reloaded, but first a one-line cell prints its shape and
   columns: an earlier turn loaded only the columns it needed, so the wavelength or Ångström column you want may
   not be in it. If it is missing, load a new frame with the columns you need instead of patching the old one.
