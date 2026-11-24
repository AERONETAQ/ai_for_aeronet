WHEN: always, in every cell that reads data. The 20 tables together are many times larger than the memory of
the sandbox, the all-points tables hold millions of rows each and the two solar AOD ones (DATA_POINTS
59 M, DATA_L15_POINTS 68 M, about 10 GB each) tens of millions: a careless load kills the kernel and loses every variable.
Loading is planned, not tried.
1. Take the smallest table that answers the question: a monthly table (0.04–0.3 M rows) before a daily one
   (0.2–1.6 M) before an all-points one (0.7–10 M, the solar AOD points 59 and 68 M). Monthly and daily
   tables answer most climatology, trend, ranking and map questions; the all-points tables are for time of day,
   single nights, single retrievals and screening by a per-retrieval quantity. The daily and monthly values
   are AERONET's own means of those points: a statistic that a daily or monthly table holds is never
   recomputed from points. DATA_POINTS and DATA_L15_POINTS are opened only for a time-of-day question
   (time_of_day skill), and always with a site filter, a time window or one aggregation.
2. Know the size before loading. In pandas a number costs 8 bytes: rows × numeric columns × 8 bytes
   (1 M rows × 10 columns = 80 MB). Text costs about 50 bytes per value: the site name of 8 M rows is about
   0.4 GB on its own, so over many sites the site name stays inside the query, as the GROUP BY key. When
   unsure, count first (instant):
     duckdb.sql(f"SELECT count(*) FROM '{DATA_ALM_L15}' WHERE AERONET_Site_Name = 'Kanpur'").fetchall()
   Keep any single frame under about 500 MB and the kernel under half of the limit printed after every cell.
3. One site, or a handful: a column list and a site filter, with either engine. The tables are stored in site
   order, so only that site's block is read:
     pd.read_parquet(DATA_LUNAR, columns=["datetime_utc", "AOD_500nm", "Lunar_Phase_Angle_Degrees"],
                     filters=[("AERONET_Site_Name", "==", "GSFC")])          # ("AERONET_Site_Name", "in", [...]) for a few sites
     duckdb.sql(f"SELECT datetime_utc, AOD_500nm FROM '{DATA_LUNAR}' WHERE AERONET_Site_Name = 'GSFC'").df()
   The busiest site of an all-points table has about 0.1 M rows: fine with a column list, never with every
   column (the tables have 71 to 497 columns). In DATA_POINTS and DATA_L15_POINTS a long-record site holds
   several times more: count first, and add a year or date filter when the question allows one.
4. Many sites, a region, the network, a whole table: one aggregation inside DuckDB, and only its result comes
   back. The query reads the file in pieces and never holds the table:
     per_site = duckdb.sql(f"""
         SELECT AERONET_Site_Name, any_value(Site_Latitude_Degrees) AS lat, any_value(Site_Longitude_Degrees) AS lon,
                count(AOD_500nm) AS n, avg(AOD_500nm) AS mean_aod, median(AOD_500nm) AS median_aod,
                quantile_cont(AOD_500nm, 0.9) AS p90_aod
         FROM '{DATA_LUNAR}' WHERE year BETWEEN 2020 AND 2024
         GROUP BY AERONET_Site_Name""").df()
   The same shape gives per site and month (GROUP BY AERONET_Site_Name, year, month), per site and night or local
   day (step 6), counts under a condition (count(*) FILTER (WHERE Coincident_AOD440nm >= 0.4)), and a first
   screening of sites (HAVING count(AOD_500nm) >= 100). A list of sites from an earlier step goes in as
   WHERE AERONET_Site_Name IN ('GSFC', 'Kanpur'), built from the Python list.
   Be efficient: a pass over a whole 10 M-row table takes a few seconds (over the solar AOD points tables
   longer in proportion: select few columns and give the cell a longer timeout), so there is never a reason to sample
   rows, to loop over sites or years in Python (each loop reads the file again), or to spread one aggregation
   over several cells. Ask one query for every statistic the step needs (count, mean, median, percentiles
   together), keep its small result as the variable, and compute from that result afterwards instead of
   querying the table again.
5. Two tables: aggregate each to the common unit first (site-day, site-night, site-month), then join the two
   small results, in the same query (WITH ... AS) or with pandas merge. Raw rows of two all-points tables are
   never joined, and two levels of one table are never loaded side by side.
6. DuckDB, the few things to know:
   - a table is its path in single quotes inside an f-string: FROM '{DATA}'; .df() gives a pandas DataFrame,
     .fetchall() a list of tuples;
   - a missing value is NULL: count(column) counts the values, count(*) the rows, avg / median / min / max skip
     the missing ones; "no data" never becomes zero;
   - the local solar day of a row (AERONET's own day, time_of_day skill) and its local hour:
       CAST(datetime_utc + to_seconds(CAST(round(Site_Longitude_Degrees * 240) AS BIGINT)) AS DATE) AS local_day
       ((epoch(datetime_utc) + Site_Longitude_Degrees * 240) % 86400) / 3600.0 AS local_hour
   - month starts: date_trunc('month', date); a time window: datetime_utc BETWEEN TIMESTAMP '2023-06-06' AND
     TIMESTAMP '2023-06-09';
   - a result column is never named with an SQL word (days, months, year, hour, date, count): write n_days,
     n_months; text values take single quotes; / is a float division;
   - a boolean is averaged as avg((condition)::INT).
7. The guard, and its limit: DuckDB has its own 2 GB limit, set when the kernel starts. A query that needs more
   (ORDER BY or a join over millions of full rows, SELECT * on an all-points table) stops with "Out of Memory
   Error", the kernel and its variables survive, and the next cell asks for less: fewer columns, an aggregation
   instead of rows, one site, one year. It is never re-run unchanged, and the limit is never raised. pandas has
   no such guard: a too-large pd.read_parquet, or .df() of a result with millions of rows, is what kills a kernel.
8. An intermediate result that is too large to keep in memory but needed again is written to /workspace as
   parquet (the workspace holds 1 GB) and read back by column. The answer names the table and says when a number
   came from an aggregation over all rows of a table (N rows, N sites), so the reader knows nothing was sampled.
