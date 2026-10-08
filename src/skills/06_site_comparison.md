WHEN: two or more sites, "compare", "regional", "which site is dustier", "difference between".
1. Compare only over the overlapping period and the same wavelength; state the common period and N days per site.
   If overlap < 2 years, compare climatologies instead and say they are from different years.
2. Report per site: coordinates, elevation, period, N, mean, median, 90th percentile of AOD 500 nm and mean AE
   440–870; then the difference of means/medians. Elevation matters: a mountain site (Mauna_Loa, Izana, > 2 km)
   sees only the free troposphere and is not comparable with a surface site nearby.
3. For paired daily differences use only days both sites have data (inner join on date).
4. Figure, when warranted: same y-axis for all sites; monthly climatology lines on one axis, or box plots per site;
   a map (maps skill: cartopy, site markers coloured by the value, site names) when there are more than 3 sites.
5. Distances between sites (haversine) belong in the answer when the user asks about "nearby".
