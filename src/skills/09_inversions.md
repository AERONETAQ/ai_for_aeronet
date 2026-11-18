WHEN: absorption, "single scattering albedo", SSA, "size distribution", "fine mode / coarse mode", "effective
radius", "refractive index", sphericity, "non-spherical", "asymmetry factor", "radiative forcing", "lidar ratio",
depolarization, "how absorbing", "what kind of particles" beyond the Ångström exponent. Tables: DATA_ALM,
DATA_ALM_L15, DATA_ALM_L15_DAILY, DATA_ALM_L15_MONTHLY (almucantar scans); DATA_INV, DATA_INV_MONTHLY,
DATA_INV_L15_MONTHLY (hybrid scans).
1. What a retrieval is (Dubovik & King 2000; Version 3: Sinyuk et al. 2020): the sky radiance measured in a
   scan at four wavelengths (440, 675, 870, 1020 nm; 443, 667, 865 or 870, 1020 on the ocean-colour
   instruments), together with the coincident AOD, is inverted into a 22-bin volume size distribution, a complex
   refractive index and a fraction of spherical particles; SSA, absorption AOD, asymmetry factor, fine/coarse
   extinction, lidar and depolarization ratios and fluxes are computed from those. Two scans feed it:
   - the almucantar (the Sun's elevation held, azimuth swept): on every instrument since 1993, several per day
     in the morning and afternoon; Level 2.0 needs a solar zenith angle >= 50°, so it never samples a high Sun;
   - the hybrid scan (Model-T instruments, since 2014): reaches the same scattering angles down to a solar
     zenith angle of 25°, so it adds retrievals nearer noon and in summer and in the tropics.
   Which table: a long record, a site without a Model-T, a network-wide absorption climatology, anything before
   2014 -> DATA_ALM (Level 2.0, one row per retrieval; make daily or monthly means with the time_of_day skill
   step 2 and the climatology rules). A Model-T site after 2014, or daily means ready made -> DATA_INV;
   DATA_INV_MONTHLY when a monthly mean is all that is asked. The two scan types are never pooled in one
   statistic; where a site has both, comparing them is a result in itself. Retrievals are a small subset of AOD
   days (a clear, homogeneous sky over the whole scan is needed): say how many retrieval days against AOD days.
2. Level 2.0 criteria shape the sample (Holben et al. 2006; Sinyuk et al. 2020): SSA, absorption AOD, the
   refractive index, lidar and depolarization ratios exist only at AOD(440) >= 0.4; size distribution, volume
   concentration, radii, asymmetry factor, extinction by mode and fluxes at any AOD; solar zenith angle >= 50°
   for the almucantar (25° for the hybrid); a sky-radiance fit residual within about 5–8 %; a minimum number of
   measured scattering angles in each angular range; and Level 2.0 input AOD. Absorption statistics therefore
   describe hazy days and seasons, not the site's average day: state the AOD threshold and compare with the
   site's AOD climatology. The AOD of a retrieval is AOD_Coincident_Input_<λ>nm (Coincident_AOD440nm in the
   all-points tables), the measurement the retrieval used, not DATA's daily mean of the whole day.
3. The Level 1.5 inversion tables are a different population, not a provisional copy. They hold every retrieval
   that ran: also low Sun angles below the Level 2.0 limit, poor fits (sky residuals of tens of percent), and
   SSA and refractive index at any AOD, where they are weakly constrained. Rules:
   - a published-quality statistic uses Level 2.0 (DATA_ALM, DATA_INV, DATA_INV_MONTHLY);
   - DATA_ALM_L15 is screened per retrieval before any use, with its two flags:
     If_Retrieval_is_L2_without_L2_0_4_AOD_440_threshold = 1 keeps the retrievals that pass every Level 2.0
     check except the AOD threshold (with If_AOD_is_L2 = 1 these are the Level 2.0 retrievals, now with SSA at
     every AOD); If_AOD_is_L2 = 0 marks retrievals whose input AOD is still Level 1.5 (the recent period, or an
     instrument that never got a final calibration);
   - absorption below the Level 2.0 threshold: flag = 1 and Coincident_AOD440nm >= 0.2 is the usual relaxed
     choice in the literature; say so, give N, and widen the uncertainty (SSA about ±0.05 near AOD(440) 0.2
     against ±0.03 at 0.4 and above; Dubovik et al. 2000); below 0.2 SSA and the refractive index are not
     interpreted at all;
   - those retrievals (If_AOD_is_L2 = 0) carry no Level 2.0 flag: keep Sky_Residual_percent <= 5–8 and solar
     zenith angle >= 50° yourself, label the result "provisional (Level 1.5)";
   - DATA_ALM_L15_DAILY and the Level 1.5 monthly tables are averages of ALL Level 1.5 retrievals, unscreened:
     use them for size and volume products, for coverage ("does this site have inversions lately") and for
     recent months; never for an SSA or refractive-index statistic, which is recomputed from the screened
     points of DATA_ALM_L15 instead.
4. Uncertainties (Dubovik et al. 2000; Sinyuk et al. 2020): SSA ±0.03 at AOD(440) >= 0.4, larger below; the
   imaginary refractive index 30–50 %; the real part ±0.04, poorly constrained for dust; the size distribution
   15–25 % between 0.1 and 7 µm, worse at both ends; fine-mode volume median radius about ±0.01 µm, coarse about
   ±0.1 µm. Report SSA to 3 decimals and never interpret an SSA difference smaller than 0.03 as real. These are
   for single retrievals; a mean over many retrievals is more precise but not more accurate (calibration and
   surface-albedo errors do not average out). Sphericity_Factor_percent is meaningful only for coarse-mode
   aerosol at moderate AOD (Dubovik et al. 2006); where it is empty or the aerosol is fine, shape shows through
   the depolarization ratio and the coarse-mode volume.
5. Interpretation (Dubovik et al. 2002 climatology; Giles et al. 2012; Russell et al. 2010):
   - SSA(440) < 0.85 strongly absorbing (black carbon: fresh smoke, urban/industrial soot); 0.85–0.92 moderately
     absorbing; > 0.95 weakly absorbing (sulfate, sea salt, aged haze). Spectral shape: SSA decreasing with
     wavelength = fine absorbing aerosol (smoke, pollution); increasing with wavelength = dust (iron oxides absorb
     the blue); flat and high = marine or sulfate.
   - Absorption Ångström exponent 440–870: about 1 = black carbon; 1.5–3 = brown carbon or dust; extinction
     Ångström exponent < 0.75 coarse (dust, sea salt), > 1.5 fine (smoke, pollution), as in the aerosol_type skill.
   - Depolarization_Ratio_440nm about 0.25–0.35 = non-spherical (dust); below 0.1 = spherical (smoke,
     pollution, sea salt); it is a model quantity, not a lidar measurement.
   - Reference values (approximate, Dubovik et al. 2002, multi-year means, SSA about ±0.03): urban-industrial — GSFC SSA(440)
     0.98 falling to 0.97 at 1020 nm, Mexico City 0.90, fine volume median radius 0.12–0.20 µm; biomass burning —
     African savanna (Zambia) SSA 0.88 at 440 nm falling to about 0.80 at 1020 nm, Amazon forest 0.93–0.94, boreal
     forest 0.94, fine radius 0.13–0.16 µm; desert dust — Bahrain / Solar Village / Cape Verde SSA 0.92–0.93 at
     440 nm rising to 0.96–0.98 at 1020 nm, coarse volume median radius 1.9–2.7 µm, extinction Ångström exponent
     0.1–0.5; oceanic (Lanai) SSA 0.98 flat, Ångström 0.3–0.7. A site mean far from every row needs a second look.
   - Size: fine-mode volume median radius 0.10–0.15 µm fresh smoke or urban, 0.15–0.25 µm aged or humidified;
     coarse mode 1.5–3 µm (dust 2 µm and larger). Fine-mode fraction of the volume = VolC_F / VolC_T; of the
     extinction = AOD_Extinction_Fine / AOD_Extinction_Total at 440 nm. Combine: high depolarization +
     coarse-dominated + SSA rising with wavelength = dust; low depolarization + fine-dominated + SSA falling =
     biomass burning or pollution; the aerosol_type skill's AOD–AE classes and these agree for most days — report when they do not.
6. Methods: a statistic is built from one table, one level, one scan type and one filter set. Climatologies and
   seasonal cycles follow the climatology skill's rules with retrieval days as the unit (months with >= 5
   retrieval days); from DATA_ALM, first the daily means by local day, then the months, so that a day with five
   retrievals does not weigh five times a day with one. A mean size distribution = the mean of each of the 22
   dVdlnr bins (missing values skipped), plotted against the bin radius on a logarithmic x-axis; the fine/coarse
   split is AERONET's (VolC_F, VolC_C, the extinction by mode; the separating radius is
   Inflection_Radius_of_Size_Distribution_um where the table has it); absorption AOD = AOD × (1 − SSA) is a
   check of the column, not a replacement. The filter sets are different channels: never average a 440 nm column
   with a 443 nm one. Which set a site has: describe_columns(site, dataset=...) for one site (a long listing: call
   it once); for many sites one query that counts both, count(Single_Scattering_Albedo_440nm) and
   count(Single_Scattering_Albedo_443nm) per site. A multi-site comparison uses one set and names the sites of
   the other set as excluded. A network-wide statistic keeps the sites with enough retrievals and enough
   retrieval days (a convention to state, e.g. >= 50 retrievals on >= 20 days).
   Trends of SSA or absorption: possible only on the long almucantar record and only with care: the
   AOD(440) >= 0.4 selection changes with the aerosol load itself (cleaner years contribute fewer and different
   days), instruments are swapped, and the uncertainty is 0.03; use the trend skill's method on yearly or
   seasonal means with N per year shown, report the number of retrievals behind each year, and call a change
   smaller than 0.03 over the record undetectable. On the hybrid record (2014 on) describe by year with N instead.
   Hybrid retrievals as single points, almucantar Level 2.0 as ready-made daily or monthly means, and the phase
   functions are not in this corpus: say so when asked for them.
7. Fluxes and forcing: Rad_Forcing_BOA is negative (less sunlight at the surface); Rad_Forcing_TOA negative =
   the aerosol cools the Earth–atmosphere column, positive = warms it (absorbing aerosol over a bright surface or
   clouds); Forcing_Eff = forcing per unit AOD at 550 nm. They are instantaneous values at the scan times, at
   the solar zenith angle of the scan (averaged over the day's scans in the daily tables), not 24-hour means:
   say so, and do not compare forcing between sites or seasons without comparing the solar zenith angles
   (Average_Solar_Zenith_Angles_for_Flux_Calculation_Degrees in the all-points tables). Lidar ratio at 440 nm:
   dust about 40–60 sr, smoke 60–90 sr, marine 20–30 sr; like the depolarization ratio (step 5) it comes from
   the retrieved spheroid model, not from a lidar.
8. Figures, when the figures skill says one is warranted: the size distribution as dV/dln r (µm³/µm²) against
   radius (µm, log axis) with the 22 bin points; an SSA spectrum as 4 points against wavelength with ±0.03 error
   bars; for aerosol typing a scatter of SSA(440) against the extinction Ångström exponent, or absorption against
   extinction Ångström exponent, coloured by season. Every panel states the scan type, the level, the AOD(440)
   selection and N (retrievals and days).
