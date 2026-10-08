WHEN: before drawing a map: "map", "where", "show the region", "spatial pattern", "which sites", a comparison of
more than 3 sites, or site locations. A map is a figure: the figures skill applies in full (last, once, from
checked numbers, self-explanatory, figure check); this adds what is special about maps of AERONET sites.
1. Sites are points, not a field. One marker per site at (Site_Longitude_Degrees, Site_Latitude_Degrees); never
   interpolate, contour or grid between sites: a few hundred sites, unevenly spread, do not define a surface.
   Give with the map the numbers nobody can read off colours: N sites, min, max, mean across sites, and the
   highest and lowest sites with their coordinates. The value per site is one checked number (a mean, a trend,
   a count of days) over one stated period and wavelength; sites with no data in that period are left off and
   counted in the answer, never drawn as zero.
2. Area: the bounding box of the sites drawn, widened by about 10 % (ax.set_extent([w, e, s, n],
   crs=ccrs.PlateCarree())), or the box of the region asked about. ccrs.PlateCarree() for regions,
   ccrs.Robinson() with ax.set_global() for the globe. A box also shows neighbouring sites: write "in and around",
   or draw the border of the area on top with ax.add_geometries([poly], crs=ccrs.PlateCarree(), facecolor="none").
3. Which sites belong to a region: for a country or state the border decides (below); for a city or a point,
   geocode gives the coordinates and nearest_sites the AERONET sites within a radius, and the map draws that
   circle's sites with the point marked. Country and state borders are in the sandbox (Natural Earth, nothing
   to download), e.g. the sites in India:
     import shapely, cartopy.io.shapereader as shpreader
     recs = list(shpreader.Reader(shpreader.natural_earth("10m", "cultural", "admin_0_countries")).records())
     poly = shapely.union_all([r.geometry for r in recs if r.attributes["ISO_A2_EH"] == "IN"])
     inside = sites[shapely.contains_xy(poly, sites["lon"], sites["lat"])]        # sites: one row per site
   Country attributes: NAME_LONG, ISO_A2_EH (two-letter code), CONTINENT, SUBREGION (UN regions, e.g. "Southern
   Asia"). States and provinces: natural_earth("10m", "cultural", "admin_1_states_provinces_lakes") with name,
   admin (the country's name) and iso_3166_2 (e.g. IN-PB). A country's border includes its overseas parts
   (France includes French Guiana): say so, or keep only the sites inside the bounding box of the mainland.
   Island and coastal sites can fall just outside a polygon: say how many sites a border test dropped and name
   them when few. One site table (name, lon, lat) is built once with drop_duplicates on the site name, not
   from the full daily table.
4. Drawing the points: ax.scatter(lon, lat, c=value, transform=ccrs.PlateCarree(), edgecolor="k", linewidth=0.3),
   sorted so the high values are drawn last; a location-only map uses one colour. Site names with ax.text when
   up to about 30 sites are drawn; above that, label only the highest and lowest. The marker size says nothing
   unless the legend defines it (e.g. size = years of record). The same symbol for every site; a site that is
   different in kind (n = 1 year, a mountain site above 2 km) gets its own marker, named in the legend.
5. Outlines, all in the sandbox: ax.coastlines("50m"), ax.add_feature(cfeature.BORDERS.with_scale("50m")), and
   cfeature.STATES, LAND, OCEAN, LAKES the same way (import cartopy.crs as ccrs, cartopy.feature as cfeature
   in the cell that draws). Scales: "110m" for the globe, "50m" for countries and continents, "10m" for states
   and cities (slower, about 10 s). Nothing else can be loaded: no rivers, no map tiles, no terrain, no
   satellite imagery. Faint LAND and OCEAN fills make small markers readable; the data stays on top (zorder).
6. Colours: a sequential colour map for a quantity (AOD, a mean, a count, SSA with a scale that spans only the
   observed range), its scale capped near the 98th percentile across the sites with extend="max" on the colour
   bar. A difference or a trend on a diverging colour map centred on zero; say in the colour bar label what
   positive means ("AOD 500 nm trend per decade, positive = increasing"; "night minus day AOD 500 nm, positive =
   more aerosol at night"; "Level 1.5 minus Level 2.0"). Sites that have the product (inversions, lunar) and
   sites that do not, when both are drawn, get two markers named in the legend; a site is never drawn as zero. The colour bar label names the quantity, wavelength and unit, as the figures skill
   asks of every axis. Several panels share one colour scale and one colour bar.
7. Latitude and longitude labels: gl = ax.gridlines(draw_labels=True, linewidth=0.2); gl.top_labels =
   gl.right_labels = False. Gridline labels break matplotlib's automatic title placement on a GeoAxes (the
   title's position becomes NaN): the title then vanishes from the PNG, and fig.savefig(..., bbox_inches="tight")
   saves only the colour bar, with the map itself missing. Verified fix in this sandbox: give the title an explicit
   position, ax.set_title("...", y=1.01) (or fig.suptitle), and the title, the labels and a tight save all work.
   fig.canvas.draw() before saving does not fix it. Keep figsize at most 10x6 in, dpi 110, as for every figure.
8. Figure check for a map, on top of the figures skill: where the highest and the lowest sites are, against the
   table; the number of markers against N; a map that is blank, one single colour, without coastlines, with the
   data outside the frame, or with the markers hidden under the land fill is a FAIL.
