"""Section 6 · Data dictionary of the 20 parquet tables under /data (notebooks/process_data/05).

Data-specific: swap this file, tools/data_tools.py and the data_access skill for another dataset.
"""

DATA_DICTIONARY = """
### data dictionary — 20 read-only parquet tables under /data (AERONET Version 3), paths pre-set in the kernel
Four products, each at two quality levels and at three time steps: monthly means, daily means and all points
(lunar AOD: all points only). Level 2.0 = quality-assured, final calibration; Level 1.5 = provisional
(data_levels skill). "points" = one row per measurement or retrieval.

variable              dataset=         product                  level  one row is     rows  sites  columns  period
DATA                  aod_l2           solar AOD                2.0    site-day     1.44 M  1,489       71  1993-05 → 2026-08
DATA_L15              aod_l15          solar AOD                1.5    site-day     1.62 M  1,612       71  1993-05 → 2026-10
DATA_MONTHLY          aod_l2_monthly   solar AOD                2.0    site-month   0.29 M  1,489       98  1993-05 → 2026-09
DATA_L15_MONTHLY      aod_l15_monthly  solar AOD                1.5    site-month   0.31 M  1,611       98  1993-05 → 2026-09
DATA_POINTS           aod_l2_points    solar AOD                2.0    measurement  58.6 M      *       97  *
DATA_L15_POINTS       aod_l15_points   solar AOD                1.5    measurement  67.7 M      *       97  *
DATA_LUNAR            lunar            lunar AOD                2.0    measurement  8.35 M    524       76  2014-12 → 2026-08
DATA_LUNAR_L15        lunar_l15        lunar AOD                1.5    measurement  10.5 M    629      ~76  2014-12 → 2026-10
DATA_INV              inv              inversions, hybrid scan  2.0    site-day     0.17 M    512      335  2014-06 → 2026-08
DATA_INV_L15_DAILY    inv_l15_daily    inversions, hybrid scan  1.5    site-day     0.32 M      *      339  *
DATA_INV_MONTHLY      inv_monthly      inversions, hybrid scan  2.0    site-month   0.04 M    624     ~490  2014 → 2026
DATA_INV_L15_MONTHLY  inv_l15_monthly  inversions, hybrid scan  1.5    site-month   0.05 M    637     ~490  2014 → 2026
DATA_INV_POINTS       inv_points       inversions, hybrid scan  2.0    retrieval    0.70 M      *      219  *
DATA_INV_L15_POINTS   inv_l15_points   inversions, hybrid scan  1.5    retrieval    1.52 M      *      220  *
DATA_ALM_DAILY        alm_daily        inversions, almucantar   2.0    site-day     0.65 M      *      335  *
DATA_ALM_L15_DAILY    alm_l15_daily    inversions, almucantar   1.5    site-day     1.06 M  1,514     ~340  1993 → 2026-10
DATA_ALM_MONTHLY      alm_monthly      inversions, almucantar   2.0    site-month   0.29 M      *      491  *
DATA_ALM_L15_MONTHLY  alm_l15_monthly  inversions, almucantar   1.5    site-month   0.28 M  1,513      497  1993-05 → 2026-10
DATA_ALM              alm              inversions, almucantar   2.0    retrieval    2.29 M  1,342     ~220  1993 → 2026
DATA_ALM_L15          alm_l15          inversions, almucantar   1.5    retrieval    4.76 M  1,514     ~220  1993 → 2026-10

* sites and period are not listed for these seven tables: list_sites(dataset=...) gives them. DATA_POINTS and
DATA_L15_POINTS are by far the largest tables, about 10 GB each on disk (the next largest is 3 GB).

Not in the corpus: lunar AOD as daily or monthly means (nights are built from the points, lunar skill), the
spectral deconvolution (fine/coarse AOD) product, the phase functions, PI contacts.

Common to every table: AERONET_Site_Name (text), Site_Latitude_Degrees, Site_Longitude_Degrees (decimal
degrees), Site_Elevation_m, date, year, month, Data_Quality_Level ("lev20" or "lev15"). Column names are
AERONET's own with ( ) [ ] - replaced by _ (and (%) by _percent). A missing value (NaN in pandas, NULL in
DuckDB) = not measured, or screened out at that level; "no data" is never zero. Tables of the same time step
join on AERONET_Site_Name + date.
- Daily tables: one row per site and day, datetime_utc = 12:00 of that date, Day_of_Year,
  AERONET_Instrument_Number (a change = instrument swap), N_<column> = how many measurements or retrievals were
  averaged into that day's value (0 -> NaN). AERONET's day is the site's local solar day (UTC + longitude/15 h),
  verified for the inversion tables: at sites far from Greenwich it is not the UTC date of the measurements.
- Monthly tables: one row per site and month, for EVERY month from the site's first to its last, most of them
  empty (about three quarters of the rows of DATA_MONTHLY hold no value): filter on the value or on
  NUM_DAYS_<column> > 0 before counting months. date = the first day of the month; no datetime_utc, Day_of_Year
  or instrument number. NUM_DAYS_<column> = days averaged, NUM_POINTS_<column> = measurements behind them. The
  monthly AOD is the unweighted mean of the daily means of the days with at least 3 measurements, given only
  when the month has at least 3 such days (verified: this reproduces every value of DATA_MONTHLY from DATA).
  A monthly table holds means only: medians, percentiles and a stricter days rule need the daily table.
- All-points tables: datetime_utc = the time of the measurement or retrieval (UTC), date/year/month its UTC
  calendar date, Day_of_Year, Day_of_Year_Fraction, AERONET_Instrument_Number; no N_ columns (nothing is averaged).

SOLAR AOD (DATA, DATA_L15, DATA_MONTHLY, DATA_L15_MONTHLY, DATA_POINTS, DATA_L15_POINTS)
- AOD_<λ>nm: 340, 380, 400, 412, 440, 443, 490, 500, 510, 532, 551, 555, 560, 620, 667, 675, 681, 709, 779,
  865, 870, 1020, 1640 (most sites: 340, 380, 440, 500, 675, 870, 1020).
- Angstrom_Exponent_<λ1>_<λ2>nm: 340_440, 380_500, 440_675, 440_870, 500_870 (440_675nm_Polar: polar instruments).
- Precipitable_Water_cm: column water vapour, cm.
- DATA is the reference; its record ends at the instrument's last post-field calibration, months to two years
  before today, site by site. DATA_L15 has the same columns and reaches the last weeks (data_levels skill).
- DATA_MONTHLY, DATA_L15_MONTHLY: AERONET's monthly means of the same quantities.
- DATA_POINTS, DATA_L15_POINTS: every measurement behind those daily means, one row per measurement (a triplet,
  minutes apart while the Sun is unobscured). The same AOD, Ångström and water-vapour columns, plus
  per-measurement columns of the kind the lunar tables have (triplet variability, zenith angle, optical air
  mass, exact wavelengths): describe_columns(dataset="aod_l2_points") lists them. When to open them:
  large_tables skill step 1.

LUNAR AOD (DATA_LUNAR Level 2.0, DATA_LUNAR_L15 Level 1.5; the same columns)
- One row per measurement (a triplet, about every 3 min while the Moon is up and bright); one night spans two
  UTC dates. DATA_LUNAR_L15 is the provisional version: more sites (629 against 524), reaching the last weeks.
- AOD_<λ>nm: 440, 500, 675, 870, 1020, 1640 on nearly every instrument (no UV at night); 412, 443, 490, 510,
  560, 667, 681, 709, 779, 865 only on ocean-colour instruments (about 4 % of rows). Precipitable_Water_cm.
- Triplet_Variability_<λ> (max − min of the three AOD values of the triplet) and
  Triplet_Variability_Precipitable_Water_cm: measurement noise, larger than by day and largest at large phase
  angle and air mass.
- Angstrom_Exponent_440_870nm, 440_675nm, 500_870nm; Angstrom_Exponent_380_500nm is computed WITHOUT a 380 nm
  channel at night (effectively 440–500 nm): prefer 440_870nm.
- Lunar_Zenith_Angle_Degrees, Optical_Air_Mass (1 = Moon at zenith, up to about 7), Lunar_Phase_Angle_Degrees
  (0 = full Moon, negative = waxing, positive = waning; measurements only within about ±90°, the bright half
  of each lunar cycle), Solar_Zenith_Angle_Degrees, Sensor_Temperature_Degrees_C, Ozone_Dobson, NO2_Dobson,
  Number_of_Wavelengths, Exact_Wavelengths_of_AOD_um_<λ>nm, Exact_Wavelengths_of_PW_um_935nm,
  Last_Date_Processed, Measurement_Type_solar_or_lunar = "lunar".
- AERONET's files repeat about 39 k rows of DATA_LUNAR verbatim (0.5 %): count measurements with
  count(DISTINCT datetime_utc) per site, or drop_duplicates(["AERONET_Site_Name", "datetime_utc"]).

INVERSIONS (hybrid scans: DATA_INV, DATA_INV_L15_DAILY, DATA_INV_MONTHLY, DATA_INV_L15_MONTHLY, DATA_INV_POINTS,
DATA_INV_L15_POINTS; almucantar scans: DATA_ALM_DAILY, DATA_ALM_L15_DAILY, DATA_ALM_MONTHLY, DATA_ALM_L15_MONTHLY,
DATA_ALM, DATA_ALM_L15; the same products in all twelve)
- Two scan types, never pooled (Retrieval_Measurement_Scan_Type = "Hybrid" or "Almucantar"; inversions skill
  step 1).
- Filter sets: spectral products come at <λ> = 440, 675, 870, 1020 nm on most instruments, or 443, 667, 865
  (or 870), 1020 nm on the ocean-colour (SeaPRISM) instruments. Every spectral product has columns for all of
  440, 443, 667, 675, 865, 870, 1020 and a site fills one set of four (describe_columns(site, dataset=...)).
- AOD_Coincident_Input_<λ>nm, Angstrom_Exponent_440_870nm_from_Coincident_Input_AOD: the measured AOD that went
  into the retrieval.
- AOD_Extinction_Total/Fine/Coarse_<λ>nm, Extinction_Angstrom_Exponent_440_870nm_Total: retrieved extinction,
  split at the fine/coarse boundary (the minimum of dV/dln r between 0.439 and 0.992 µm:
  Inflection_Radius_of_Size_Distribution_um, where the table has it).
- Single_Scattering_Albedo_<λ>nm (0–1; 1 = no absorption), Absorption_AOD_<λ>nm (= AOD × (1 − SSA)),
  Absorption_Angstrom_Exponent_440_870nm, Refractive_Index_Real_Part_<λ>nm (1.33–1.6),
  Refractive_Index_Imaginary_Part_<λ>nm (0.0005–0.5), Lidar_Ratio_<λ>nm (sr), Depolarization_Ratio_<λ>nm.
  In the Level 2.0 tables these exist only at AOD(440) >= 0.4; in the Level 1.5 tables at any AOD, unscreened
  (inversions skill step 3).
- Asymmetry_Factor_Total/Fine/Coarse_<λ>nm (mean cosine of the scattering angle).
- dVdlnr_<r>um, 22 columns: volume size distribution dV/dln r (µm³/µm²) at bin radius r µm, r = 0.050000,
  0.065604, 0.086077, 0.112939, 0.148184, 0.194429, 0.255105, 0.334716, 0.439173, 0.576227, 0.756052, 0.991996,
  1.301571, 1.707757, 2.240702, 2.939966, 3.857452, 5.061260, 6.640745, 8.713145, 11.432287, 15.000000
  (the decimal point is written _ : dVdlnr_0_050000um; radius back from the name:
  float(c[7:-2].replace("_", ".")) ).
- VolC_T/F/C (volume concentration, µm³/µm²), REff_T/F/C (effective radius, µm), VMR_T/F/C (volume median
  radius, µm), Std_T/F/C (width, std of ln r): T = total, F = fine, C = coarse mode.
- Flux_Down/Up_BOA/TOA, Diffuse_BOA/TOA (broadband 0.2–4 µm, W/m²), Rad_Forcing_BOA/TOA (W/m², negative =
  cooling), Forcing_Eff_BOA/TOA (W/m² per unit AOD at 550 nm), Spectral_Flux_Down/Up/Diffuse_<λ>nm (W/m²/µm),
  Minimum/Maximum_Altitude_For_Flux_Calculations_km.
- Sphericity_Factor_percent (retrieved share of spherical particles, %): filled mainly in the almucantar
  Level 1.5 tables (inversions skill step 4).
- Only in the all-points tables (DATA_ALM, DATA_ALM_L15; DATA_INV_POINTS and DATA_INV_L15_POINTS have the same
  kind of columns, describe_columns confirms the names), per retrieval: Coincident_AOD440nm (the AOD at the
  scan), Solar_Zenith_Angle_for_Measurement_Start_Degrees, Sky_Residual_percent (misfit of the sky radiances;
  Level 2.0 keeps <= 8 %), Sun_Residual_percent, Scattering_Angle_Bin_<range>_<λ>nm (sky radiances measured
  per scattering-angle range), Surface_Albedo_<λ>m (assumed surface albedo; the name ends in m, not nm),
  Average_Solar_Zenith_Angles_for_Flux_Calculation_Degrees, Last_Processing_Date_dd_mm_yyyy and
  Last_Processing_Time_hh_mm_ss (text), and two flags, always 1 in a Level 2.0 table and the way to screen a Level 1.5 one:
  If_Retrieval_is_L2_without_L2_0_4_AOD_440_threshold (1 = passes every Level 2.0 check except the AOD
  threshold) and If_AOD_is_L2 (1 = the input AOD is Level 2.0).
list_sites, describe_columns and nearest_sites take dataset = one of the 20 names above (default "aod_l2");
site_coverage(site) spans all 20. The sandbox environment block lists the tables actually mounted.
"""
