import cartopy
from cartopy.io import shapereader

cartopy.config["data_dir"] = "/opt/cartopy"      # where shapereader.natural_earth() saves what it downloads

LAYERS = [("physical", "coastline"),                       # ax.coastlines(), cfeature.COASTLINE
          ("physical", "land"),                            # cfeature.LAND
          ("physical", "ocean"),                           # cfeature.OCEAN
          ("physical", "lakes"),                           # cfeature.LAKES
          ("cultural", "admin_0_boundary_lines_land"),     # cfeature.BORDERS (country borders, lines)
          ("cultural", "admin_0_countries"),               # country polygons with names: which sites lie in a country
          ("cultural", "admin_1_states_provinces_lakes")]  # cfeature.STATES; state/province polygons with names

for resolution in ("110m", "50m", "10m"):
    for category, name in LAYERS:
        path = shapereader.natural_earth(resolution=resolution, category=category, name=name)
        print("downloaded", path)
