WHEN: absorption, "single scattering albedo", SSA, "size distribution", "fine mode / coarse mode", "effective
radius", "refractive index", sphericity, "non-spherical", "asymmetry factor", "radiative forcing", "lidar ratio",
depolarization, "how absorbing", "what kind of particles" beyond the Ångström exponent. Table: DATA_INV.
1. What a row is: the daily mean of that day's Level 2.0 retrievals from hybrid sky scans (Dubovik & King 2000;
   Version 3: Sinyuk et al. 2020). The retrieval inverts the sky radiance at 440, 675, 870 and 1020 nm (443, 667,
   865, 1020 on the 27 ocean-colour instruments) together with the coincident AOD into a 22-bin volume size
   distribution, a complex refractive index and a fraction of spherical particles; SSA, absorption AOD, asymmetry
   factor, fine/coarse extinction, lidar and depolarization ratios and fluxes are computed from those. N_<column>
   is the number of retrievals behind the day's value. Retrieval days are a small subset of AOD days (a clear sky
   over the whole scan is needed): say how many inversion days against AOD days in the period.
2. Level 2.0 criteria shape the sample (Holben et al. 2006; Sinyuk et al. 2020): SSA, absorption AOD and the
   refractive index exist only on days with AOD(440) >= 0.4; size distribution, volume concentration, radii and
   asymmetry factor at any AOD >= 0.02; sky-radiance fit residual within about 5–8 %; hybrid scans need a solar
   zenith angle >= 25° (minimum scattering angle 100°; the almucantar needs >= 50°, which is why hybrid
   retrievals reach closer to noon and into summer). Absorption statistics therefore describe hazy days and
   seasons, not the site's average day: state the AOD threshold and compare with the site's AOD climatology.
   The AOD of a retrieval day is AOD_Coincident_Input_<λ>nm (the measurement the retrieval used), not DATA's
   daily mean, which averages the whole day.
3. Uncertainties (Dubovik et al. 2000; Sinyuk et al. 2020): SSA ±0.03 at AOD(440) >= 0.4, larger below; the
   imaginary refractive index 30–50 %; the real part ±0.04, poorly constrained for dust; the size distribution
   15–25 % between 0.1 and 7 µm, worse at both ends; fine-mode volume median radius about ±0.01 µm, coarse about
   ±0.1 µm. Report SSA to 3 decimals and never interpret an SSA difference smaller than 0.03 as real. The
   hybrid daily product carries no sphericity fraction (AERONET leaves it at -999): particle shape shows only
   through the depolarization ratio, computed from the retrieved spheroid fraction, and the coarse-mode volume.
4. Interpretation (Dubovik et al. 2002 climatology; Giles et al. 2012; Russell et al. 2010):
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
5. Methods: climatologies and seasonal cycles from the daily rows of the inversion table with the climatology
   skill's rules (months with >= 5 retrieval days); a mean size distribution = the mean of each of the 22 dVdlnr
   bins (NaN-skipping), plotted against the bin radius on a logarithmic x-axis; the fine/coarse split is
   AERONET's (VolC_F, VolC_C, the extinction by mode), the separating radius is not reported; absorption AOD =
   AOD_Coincident_Input × (1 − SSA) is a check of the column,
   not a replacement. The two filter sets are different channels: never average a 440 nm column with a 443 nm
   one; describe_columns(site, dataset="inv") shows which set a site has; a multi-site comparison uses one set
   and names the sites of the other set as excluded. Trends of SSA or refractive index are rarely warranted: the
   AOD(440) >= 0.4 selection, the short record (2014 on) and instrument swaps confound them; describe by year
   with N instead. Almucantar-scan inversions, Level 1.5 inversions and the phase functions are not in this
   corpus: say so when asked for them.
6. Fluxes and forcing: Rad_Forcing_BOA is negative (less sunlight at the surface); Rad_Forcing_TOA negative =
   the aerosol cools the Earth–atmosphere column, positive = warms it (absorbing aerosol over a bright surface or
   clouds); Forcing_Eff = forcing per unit AOD at 550 nm. They are instantaneous values at the scan times
   averaged over the day's scans, not 24-hour means: say so. Lidar ratio at 440 nm: dust about 40–60 sr, smoke
   60–90 sr, marine 20–30 sr; depolarization ratio about 0.25–0.35 for dust, < 0.1 for spherical aerosol. Both
   come from the retrieved spheroid model, they are not lidar measurements.
7. Figures, when the figures skill says one is warranted: the size distribution as dV/dln r (µm³/µm²) against
   radius (µm, log axis) with the 22 bin points; an SSA spectrum as 4 points against wavelength with ±0.03 error
   bars; for aerosol typing a scatter of SSA(440) against the extinction Ångström exponent, or absorption against
   extinction Ångström exponent, coloured by season. Every panel states the AOD(440) >= 0.4 selection and N days.
