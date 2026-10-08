"""Section 6 · Data dictionary of the four parquet tables under /data (notebooks/process_data/01–04).

Data-specific: swap this file, tools/data_tools.py and the data_access skill for another dataset.
"""

DATA_DICTIONARY = """
### data dictionary — four read-only parquet tables under /data (AERONET Version 3), paths pre-set in the kernel
Column names are AERONET's own with ( ) [ ] - replaced by _ (and (%) by _percent). Every table has
AERONET_Site_Name (str), Site_Latitude_Degrees, Site_Longitude_Degrees (decimal degrees), Site_Elevation_m (m),
datetime_utc, date (datetime), year, month, Day_of_Year, AERONET_Instrument_Number (changes = instrument swap),
Data_Quality_Level, PI, PI_Email (site principal investigator). NaN = not measured or did not pass that level's
screening; "no data" is never zero. Tables join on AERONET_Site_Name + date.

1. DATA = /data/AERONET_AOD_L2_Daily_V3.parquet — solar AOD, Level 2.0 (cloud-screened, quality-assured, final
   calibration), daily means, one row per site and day, 1,485 sites, 1993 → the last post-field calibration,
   which ends the record a few months to two years before today, site by site. ~1.4 M rows × 73 columns.
   datetime_utc = 12:00 UTC.
   - AOD_<λ>nm: 340, 380, 400, 412, 440, 443, 490, 500, 510, 532, 551, 555, 560, 620, 667, 675, 681, 709, 779,
     865, 870, 1020, 1640 (most sites: 340, 380, 440, 500, 675, 870, 1020).
   - Angstrom_Exponent_<λ1>_<λ2>nm: 340_440, 380_500, 440_675, 440_870, 500_870 (440_675nm_Polar: polar instruments).
   - Precipitable_Water_cm: column water vapour, cm.
   - N_<column>: measurements averaged into that day's value (0 -> NaN). Data_Quality_Level = "lev20".
2. DATA_L15 = /data/AERONET_AOD_L15_Daily_V3.parquet — solar AOD, Level 1.5 (cloud-screened and quality-controlled,
   pre-field calibration only: near-real-time, provisional, "may change"), daily means, 1,613 sites, 1993 → a few days
   ago. Same 73 columns as DATA; Data_Quality_Level = "lev15". A site-day in DATA is normally also in DATA_L15 with
   a slightly different value (the final calibration); DATA_L15 additionally holds the recent months and the
   instruments that never got a final calibration.
3. DATA_INV = /data/AERONET_INV_Hybrid_L2_Daily_V3.parquet — aerosol inversion products from hybrid sky scans,
   Level 2.0, daily means of that day's retrievals, 504 sites (Model-T instruments), 2014 → a few months ago,
   ~163 k rows × 337 columns; a site has inversions on far fewer days than AOD, and SSA / absorption / refractive
   index only on days with AOD(440) >= 0.4 (none at clean sites such as Mauna_Loa). Spectral products come at
   <λ> = 440, 675, 870, 1020 nm for most instruments OR 443, 667, 865, 1020 nm for the 27 ocean-colour (SeaPRISM)
   instruments: every spectral product has both sets of columns and a site fills one set (check with
   describe_columns(site, dataset="inv")).
   - AOD_Coincident_Input_<λ>nm, Angstrom_Exponent_440_870nm_from_Coincident_Input_AOD: the measured AOD that went
     into the retrieval (only days with Level 2.0 AOD; inversion days are a subset of DATA's days).
   - AOD_Extinction_Total/Fine/Coarse_<λ>nm, Extinction_Angstrom_Exponent_440_870nm_Total: retrieved extinction,
     split at the fine/coarse boundary (the minimum of dV/dln r between 0.439 and 0.992 µm; the radius itself
     is not reported in this product).
   - Single_Scattering_Albedo_<λ>nm (0–1; 1 = no absorption), Absorption_AOD_<λ>nm (= AOD × (1 − SSA)),
     Absorption_Angstrom_Exponent_440_870nm.
   - Refractive_Index_Real_Part_<λ>nm (1.33–1.6), Refractive_Index_Imaginary_Part_<λ>nm (0.0005–0.5).
   - Asymmetry_Factor_Total/Fine/Coarse_<λ>nm (mean cosine of the scattering angle).
   - No sphericity fraction in this product (AERONET fills it with -999 for hybrid daily means): non-sphericity
     shows as a high Depolarization_Ratio and a coarse-dominated size distribution.
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
   - Lidar_Ratio_<λ>nm (sr), Depolarization_Ratio_<λ>nm.
   - N_<column>: retrievals averaged into that day's value (0 -> NaN). Data_Quality_Level = "lev20",
     Retrieval_Measurement_Scan_Type = "Hybrid", Day_of_Year_fraction.
4. DATA_LUNAR = /data/AERONET_Lunar_AOD_L2_AllPoints_V3.parquet — lunar (night-time) AOD, Level 2.0, ALL POINTS:
   one row per measurement (a triplet, every ~3 min while the Moon is up and bright), not daily means, 523 sites,
   2015 → ~3 months ago, ~8.3 M rows × 78 columns (read columns and sites selectively: never the whole table).
   datetime_utc = the measurement time; date/year/month are its UTC calendar date, so one night spans two dates.
   - AOD_<λ>nm: 440, 500, 675, 870, 1020, 1640 on nearly every instrument (no UV at night); 412, 443, 490, 510,
     560, 667, 681, 709, 779, 865 only on ocean-colour instruments (~4 % of rows). Precipitable_Water_cm.
   - Triplet_Variability_<λ> (max − min of the three AOD values of the triplet, unitless) and
     Triplet_Variability_Precipitable_Water_cm: measurement noise, larger than by day and largest at large phase
     angle and air mass.
   - Angstrom_Exponent_440_870nm, 440_675nm, 500_870nm; Angstrom_Exponent_380_500nm is computed WITHOUT a 380 nm
     channel at night (effectively 440–500 nm): prefer 440_870nm.
   - Lunar_Zenith_Angle_Degrees, Optical_Air_Mass (1 = Moon at zenith, up to ~7), Lunar_Phase_Angle_Degrees
     (0 = full Moon, negative = waxing, positive = waning; measurements only within about ±90°, the bright half
     of each lunar cycle), Sensor_Temperature_Degrees_C, Ozone_Dobson, NO2_Dobson, Number_of_Wavelengths,
     Exact_Wavelengths_of_AOD_um_<λ>nm, Exact_Wavelengths_of_PW_um_935nm, Last_Date_Processed,
     Measurement_Type_solar_or_lunar = "lunar", Data_Quality_Level = "lev20". No N_ columns (nothing is averaged).
   - AERONET's files repeat ~38 k rows verbatim (0.5 %): drop_duplicates(["AERONET_Site_Name", "datetime_utc"])
     before counting measurements.
list_sites, describe_columns and nearest_sites take dataset = "aod_l2" (DATA, the default), "aod_l15", "inv" or
"lunar"; site_coverage(site) spans all four. The sandbox environment block lists the tables actually mounted.
"""
