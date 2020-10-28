# pyportall

Python SDK to Portall

## Installation

Installing is straightforward (you may want to replace `ssh` by `https` depending on your preference):

```
$ pip install -e git+ssh://git@github.com/inspide/pyportall.git@0.0.3#egg=pyportall
```

Or, as part of your `requirements.txt` file:

```
...
-e git+ssh://git@github.com/inspide/pyportall.git@0.0.3#egg=pyportall
...
```

Currently, GeoPandas is required for this SDK to work. We may release a standalone SDK version in the future.

## Authentication

Your can use the `API_KEY` environment variable to store your API key to Portall for the Python SDK to work, or pass it to `APIClient` when instantiating the API client.

## Usage example

A similar result could have been achived using Geopandas. We will use one isovists instead of one isovist and one isoline for simplicity's sake. By the way, regular polygons could also be used both here and in the previous example directly.

```python
import pandas as pd
import geopandas as gpd

from pyportall.api.engine.core import APIClient
from pyportall.api.models.lbs import GeocodingOptions
from pyportall.api.engine.geopandas import GeocodingHelper, IsolineHelper, IsovistHelper, IndicatorHelper
from pyportall.api.models.indicators import DayOfWeek, Indicator, Moment, Month


client = APIClient(api_key="MY_API_KEY")  # API key can also be automatically detected from the PYPORTALL_API_KEY enviroment variable; a batch boolean is also available (defaults to False) to avoid timeouts

addresses = pd.DataFrame({"street": ["gran via 46", "calle alcalá 10"], "city": ["Madrid", "Madrid"]})
# addresses
#             street    city
# 0      gran via 46  Madrid
# 1  calle alcalá 10  Madrid

geocoding_helper = GeocodingHelper(client)
geocodings = geocoding_helper.resolve(addresses, options=GeocodingOptions(country="Spain"))
# geocodings
#                     geometry country state county    city district postal_code           street
# 0  POINT (-3.70587 40.42048)   Spain  None   None  Madrid     None        None      gran via 46
# 1  POINT (-3.37825 40.47281)   Spain  None   None  Madrid     None        None  calle alcalá 10

isoline_helper = IsolineHelper(client)
isolines = isoline_helper.resolve(gpd.GeoDataFrame({"geometry": geocodings["geometry"], "mode": "pedestrian", "range_s": 200}, crs="EPSG:4326"))
# isolines
#                                             geometry                                        destination        mode  range_s moment
# 0  POLYGON ((-3.70711 40.42145, -3.70668 40.42162...  {'coordinates': [-3.70587, 40.42048], 'type': ...  pedestrian      200   None
# 1  POLYGON ((-3.37975 40.47380, -3.37967 40.47432...  {'coordinates': [-3.37825, 40.47281], 'type': ...  pedestrian      200   None

isovist_helper = IsovistHelper(client)
isovists = isovist_helper.resolve(gpd.GeoDataFrame({"geometry": geocodings["geometry"]}, crs="EPSG:4326"))
# isovists
#                                             geometry                                        destination  radius_m  num_rays  heading_deg  fov_deg
# 0  POLYGON ((-3.70587 40.42087, -3.70586 40.42088...  {'coordinates': [-3.70587, 40.42048], 'type': ...       150        -1            0      360
# 1  POLYGON ((-3.37825 40.47294, -3.37825 40.47295...  {'coordinates': [-3.37825, 40.47281], 'type': ...       150        -1            0      360

indicator_helper = IndicatorHelper(client)

isovist_results = indicator_helper.resolve_aggregated(isovists, indicator=Indicator(code="pop"), moment=Moment(dow=DayOfWeek.monday, month=Month.february, hour=15))
# isovist_results
#                                             geometry                                        destination  fov_deg  heading_deg  num_rays  radius_m  value
# 0  POLYGON ((-3.70587 40.42087, -3.70586 40.42088...  {'coordinates': [-3.70587, 40.42048], 'type': ...      360            0        -1       150    969
# 1  POLYGON ((-3.37825 40.47294, -3.37825 40.47295...  {'coordinates': [-3.37825, 40.47281], 'type': ...      360            0        -1       150     80

isoline_results = indicator_helper.resolve_aggregated(isolines, indicator=Indicator(code="pop"), moment=Moment(dow=DayOfWeek.monday, month=Month.february, hour=10))
# isoline_results
#                                             geometry                                        destination        mode moment  range_s  value
# 0  POLYGON ((-3.70711 40.42145, -3.70668 40.42162...  {'coordinates': [-3.70587, 40.42048], 'type': ...  pedestrian   None      200  42034
# 1  POLYGON ((-3.37975 40.47380, -3.37967 40.47432...  {'coordinates': [-3.37825, 40.47281], 'type': ...  pedestrian   None      200   5784

isovist_disaggregated_results = indicator_helper.resolve_disaggregated(isovists["geometry"][0], indicator=Indicator(code="pop", aggregated=False), moment=Moment(dow=DayOfWeek.monday, month=Month.february, hour=15))
# isovist_disaggregated_results
#                                             geometry                  id       value  weight
# 0  POLYGON ((-3.70606 40.42066, -3.70618 40.42063...  631507574769340927  157.692308       1
# 1  POLYGON ((-3.70584 40.42064, -3.70596 40.42060...  631507574769341439  250.000000       1
# 2  POLYGON ((-3.70593 40.42080, -3.70604 40.42076...  631507574769343487  123.076923       1
# 3  POLYGON ((-3.70571 40.42077, -3.70583 40.42074...  631507574769495551  296.153846       1
# 4  POLYGON ((-3.70579 40.42094, -3.70591 40.42090...  631507574769510399  142.307692       1

isoline_disaggregated_results = indicator_helper.resolve_disaggregated(isolines["geometry"][0], indicator=Indicator(code="pop", aggregated=False), moment=Moment(dow=DayOfWeek.monday, month=Month.february, hour=15))
# isoline_disaggregated_results
#                                               geometry                  id       value  weight
# 0    POLYGON ((-3.70621 40.42176, -3.70633 40.42172...  631507574768870911  134.615385       1
# 1    POLYGON ((-3.70648 40.41948, -3.70660 40.41945...  631507574769392639   88.461538       1
# 2    POLYGON ((-3.70509 40.42116, -3.70521 40.42112...  631507574769484799  300.000000       1
# 3    POLYGON ((-3.70504 40.42146, -3.70515 40.42142...  631507574769506303  146.153846       1
# 4    POLYGON ((-3.70529 40.41995, -3.70541 40.41992...  631507574769377791  157.692308       1
# ..                                                 ...                 ...         ...     ...
# 259  POLYGON ((-3.70557 40.41891, -3.70569 40.41887...  631507574769420287  103.846154       1
# 260  POLYGON ((-3.70574 40.41924, -3.70586 40.41920...  631507574769420799  103.846154       1
# 261  POLYGON ((-3.70541 40.42058, -3.70552 40.42054...  631507574769494015  346.153846       1
# 262  POLYGON ((-3.70589 40.42033, -3.70601 40.42030...  631507574769327615  276.923077       1
# 263  POLYGON ((-3.70531 40.41919, -3.70542 40.41915...  631507574769425919  192.307692       1

# [264 rows x 4 columns]
```
