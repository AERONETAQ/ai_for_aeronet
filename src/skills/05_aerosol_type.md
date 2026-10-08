WHEN: "what kind of aerosol", "dust or smoke", "fine vs coarse", "Ångström exponent", "AOD at 550 nm".
1. Use the Angstrom_Exponent_440_870nm column (computed per measurement from the spectral AOD, then averaged);
   do not recompute it from daily-mean AODs unless it is missing.
2. Interpretation (rule of thumb, Eck et al. 1999; Dubovik et al. 2002): AE < 0.75 -> coarse-mode dominated
   (desert dust, sea salt); AE > 1.5 -> fine-mode dominated (smoke, urban/industrial pollution); 0.75–1.5 -> mixed.
   Combined with AOD: high AOD (>= 0.4 at 500 nm) & low AE = dust event; high AOD & high AE = biomass burning or
   pollution; low AOD (< 0.1) & low AE = clean marine or background.
3. AE is noisy when AOD is low: exclude days with AOD_440nm < 0.15 before classifying, and say how many days that
   removed.
   Spectral curvature as a second clue (Eck et al. 1999; Schuster et al. 2006): for fine-mode aerosol the AOD
   spectrum is concave, the exponent grows with wavelength (Angstrom_Exponent_500_870nm > Angstrom_Exponent_340_440nm
   or 440_675nm); coarse-dominated dust gives a flat spectrum with the exponents equal or the short-wavelength one
   larger. Use it only where both pairs exist and AOD(440) >= 0.15, as a qualitative check of the class.
4. Always report the table of the fraction of days in each class; when a figure is warranted, the AOD–AE scatter
   (x = AE 440–870, y = AOD 500 nm, log y), colored by month or season. This is a classification of daily means,
   not of single plumes.
5. When the site has inversions (DATA_INV, inversions skill), confirm the type with them on the same days: dust =
   high depolarization ratio, coarse-dominated volume, SSA rising with wavelength; smoke or pollution = low
   depolarization, fine-dominated, SSA falling with wavelength, SSA(440) below about 0.9 for fresh smoke. Say when the AOD–AE class
   and the inversion disagree. At night (DATA_LUNAR) only the AOD–AE route exists.
6. A fine/coarse split of the AOD itself (the spectral deconvolution product, O'Neill et al. 2003) is not in
   this corpus: the fine and coarse extinction come from the inversion table (AOD_Extinction_Fine/Coarse), on
   inversion days only. Do not implement the deconvolution from four wavelengths; say the product is absent.
7. AOD at a wavelength that is not measured (e.g. 550 nm): Ångström power law
   AOD(l) = AOD(500) * (l/500) ** (-AE) with AE = Angstrom_Exponent_440_870nm; valid only for 440–870 nm.
   Say that the value is interpolated.
