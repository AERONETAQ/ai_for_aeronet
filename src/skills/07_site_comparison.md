WHEN: two or more sites, "compare", "regional", "which site is dustier", "difference between".
1. Compare only over the overlapping period, the same table and level, and the same wavelength (inversions: the
   same filter set, 440/675/870 or 443/667/865 nm); state the common period and N days per site. If overlap
   < 2 years, compare climatologies instead and say they are from different years.
2. Report per site: coordinates, elevation, period, N, mean, median, 90th percentile of AOD 500 nm and mean AE
   440–870; then the difference of means/medians. Elevation matters: a mountain site (Mauna_Loa, Izana, > 2 km)
   sees only the free troposphere and is not comparable with a surface site nearby.
3. For paired daily differences use only days both sites have data (inner join on date); report the median
   difference with N pairs and, when a significance is asked, the Wilcoxon signed-rank test
   (scipy.stats.wilcoxon) on the paired differences, or the Mann–Whitney U test (scipy.stats.mannwhitneyu) for
   two unpaired records. A significant difference smaller than the AOD accuracy (0.01–0.02) is reported as
   "statistically significant but within measurement accuracy".
4. Figure, when warranted: same y-axis for all sites; monthly climatology lines on one axis, or box plots per site;
   a map (maps skill: cartopy, site markers coloured by the value, site names) when there are more than 3 sites.
5. Distances between sites, or from a geocoded point to the sites, belong in the answer when the user asks
   about "nearby": nearest_sites gives them for one point and one table; for anything else (site-to-site, many
   points, a selection inside run_python) the haversine distance (Earth radius 6371 km), on the one-row-per-site table,
     lat1, lon1, lat2, lon2 = np.radians(lat1), np.radians(lon1), np.radians(sites["lat"]), np.radians(sites["lon"])
     h = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
     sites["km"] = 2 * 6371.0 * np.arcsin(np.sqrt(h))
   then sort by km and keep the radius asked for; say the radius and how many sites it holds.
