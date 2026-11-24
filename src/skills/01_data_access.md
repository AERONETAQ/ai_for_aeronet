WHEN: the first step of every analysis, before any statistic.
1. Which table answers the question (the data dictionary lists all 20; one level and one scan type per statistic):
   - solar AOD over many sites or many years, where a monthly mean is enough (climatology, trend, ranking, map)
     -> DATA_MONTHLY, AERONET's own monthly means, a small table; daily values, episodes, medians and
     percentiles, paired comparisons, a monthly rule of your own -> DATA (Level 2.0 daily means, the reference);
     the hour of the day, the hours inside one day, the AOD at a given time (a satellite overpass) ->
     DATA_POINTS with the time_of_day skill, and for nothing that a daily mean answers;
   - the recent months, "latest", a site or period missing from Level 2.0 -> DATA_L15 or DATA_L15_MONTHLY with the
     data_levels skill;
   - absorption, size, shape, refractive index, forcing -> the inversion tables with the inversions skill:
     the almucantar tables (1993 →, the widest network) for long records and most sites, the hybrid tables
     (2014 →) for the Model-T instruments and for retrievals nearer noon. In either family the monthly table
     (DATA_ALM_MONTHLY, DATA_INV_MONTHLY) where a monthly mean is enough, the daily one (DATA_ALM_DAILY,
     DATA_INV) otherwise, the points (DATA_ALM, DATA_INV_POINTS) only for single retrievals, the time of day
     or a screening by a per-retrieval quantity; the Level 1.5 versions as that skill says;
   - night, lunar, day–night -> DATA_LUNAR (DATA_LUNAR_L15 for the recent months) with the lunar skill;
   - time of day, single retrievals or measurements -> the all-points tables with the time_of_day skill;
   - water vapour -> the water_vapour skill (solar tables and lunar).
   A cross-table question brings each table to a common unit first (site-day, site-night, site-month), joins on
   AERONET_Site_Name + date, and names each table, its level and its scan type in the answer.
2. Find the site and what it has with the tools, as the rules above say: list_sites for the exact name
   (case-sensitive, underscores: "Mauna_Loa"), site_coverage(site) for its spans in all 20 tables,
   describe_columns(site, dataset=...) for its wavelengths or products. Then load only what the question needs,
   as the large_tables skill says.
3. Describe the record before using it: days (nights, retrievals, months) per year, gaps, and the coverage of the
   wavelength or product you chose (every column is empty where it was not measured or failed that level's
   screening). Coverage is uneven: instruments are moved, break, and are recalibrated; gaps are normal, not
   errors. The records of one site have different spans: Level 2.0 ends months to two years before Level 1.5
   (site by site); almucantar inversions start in 1993, hybrid ones in 2014, and both hold far fewer days than
   AOD; the lunar record starts in 2015 and covers half of each month; a monthly table has a row for every
   month of the site's span, most of them empty.
4. What one row is (a day, a month, a measurement or a retrieval) and its count columns are in the data
   dictionary. A day with N=1 is a real but weak estimate: say so if it matters.
5. Level 2.0 is already cloud-screened and quality-assured (Version 3, Giles et al. 2019): no extra cloud
   screening and no "cleaning" of outliers (aod_measurement skill). Level 1.5 is not only "less calibrated":
   for inversions it is unscreened (data_levels and inversions skills).
6. Wavelengths: 500 nm is the standard reporting wavelength; 440/675/870/1020 nm are on nearly every instrument
   (the ocean-colour ones carry 443/667/865 instead); 340/380 nm and 1640 nm only on some, never at night;
   AOD_531nm, AOD_551nm etc. are rarely populated. Check before use.
