# Examples

## Simple, generic usage example

This is a very simple example that outlines how the different components work and interact with each other. The problem we will be trying to solve is understanding how many people can be counted on a Friday in February from 3pm to 4pm in the surroundings of two given locations.

First of all, let us do the imports:

```python
import pandas as pd
import geopandas as gpd

from pyportall.api.engine.core import APIClient
from pyportall.api.models.lbs import GeocodingOptions
from pyportall.api.engine.geopandas import GeocodingHelper, IsolineHelper, IsovistHelper, IndicatorHelper
from pyportall.api.models.indicators import DayOfWeek, Indicator, Moment, Month
```

Next, we need the [API client][pyportall.api.engine.core.APIClient] to provide the helper components with the capability to send authenticated (technically, metadata requests do not require authentication, but this behavior may change in the future anyway) requests:

```python
client = APIClient(api_key="MY_API_KEY")  # API key can also be automatically detected from the PYPORTALL_API_KEY enviroment variable; a batch boolean is also available (defaults to False) to avoid timeouts
```

As a starting point for our actual analysis, let us build a [DataFrame](https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html#dataframe) with the two addresses we want to work with:

```python
addresses = pd.DataFrame({"street": ["Gran Vía 46", "Calle Alcalá 10"], "city": ["Madrid", "Madrid"]})
# addresses:
#             street    city
# 0      gran via 46  Madrid
# 1  calle alcalá 10  Madrid
```

We need to translate, i.e. geocode, those addreses into their corresponding longitude and latitude coordinates before we can actually do anything useful with them:


```python
geocoding_helper = GeocodingHelper(client)
geocodings = geocoding_helper.resolve(addresses, options=GeocodingOptions(country="Spain"))
# geocodings:
#                     geometry country state county    city district postal_code           street
# 0  POINT (-3.70587 40.42048)   Spain  None   None  Madrid     None        None      gran via 46
# 1  POINT (-3.37825 40.47281)   Spain  None   None  Madrid     None        None  calle alcalá 10
```

Now we have a [GeoDataFrame](https://geopandas.org/data_structures.html#geodataframe) object with a `geometry` column that contains the actual coordinates that correspond to the input addresses, plus other columns with the actual input parameters.

Note how we have used a [GeocodingOptions][pyportall.api.models.lbs.GeocodingOptions] object to set defaults for all the addresses. We could have added "Madrid" as a default option too, instead of repeating it for both addresses as we just did.

We will define two different "surroundings" for each location: one will be the area that can be reached in less than a 200-second walk from the given point ("isoline"), and the other will be the visible area in all directions from that spot (i.e., considering buildings as obstacles) up to 150 meters ("isovist").

Let us define and compute such areas:

```python
isoline_helper = IsolineHelper(client)
isolines = isoline_helper.resolve(gpd.GeoDataFrame({"geometry": geocodings["geometry"], "mode": "pedestrian", "range_s": 200}, crs="EPSG:4326"))
# isolines:
#                                             geometry                                        destination        mode  range_s moment
# 0  POLYGON ((-3.70711 40.42145, -3.70668 40.42162...  {'coordinates': [-3.70587, 40.42048], 'type': ...  pedestrian      200   None
# 1  POLYGON ((-3.37975 40.47380, -3.37967 40.47432...  {'coordinates': [-3.37825, 40.47281], 'type': ...  pedestrian      200   None

isovist_helper = IsovistHelper(client)
isovists = isovist_helper.resolve(gpd.GeoDataFrame({"geometry": geocodings["geometry"]}, crs="EPSG:4326"), options=IsovistOptions(radius_m=100))
# isovists:
#                                             geometry                                        destination  radius_m  num_rays  heading_deg  fov_deg
# 0  POLYGON ((-3.70587 40.42087, -3.70586 40.42088...  {'coordinates': [-3.70587, 40.42048], 'type': ...       100        -1            0      360
# 1  POLYGON ((-3.37825 40.47294, -3.37825 40.47295...  {'coordinates': [-3.37825, 40.47281], 'type': ...       100        -1            0      360
```

Much like with geocoding above, we could have used [IsolineOptions][pyportall.api.models.lbs.IsolineOptions] and/or [IsovistOptions][pyportall.api.models.lbs.IsovistOptions] to set default input parameters.

In any case, the resulting geodataframes contain the geometry that correspond to the computed areas of interest, plus other columns with the actual input parameters.

Now let us find the people count (indicator code "pop") we are interested in for all four areas:

```python
indicator_helper = IndicatorHelper(client)

isovist_results = indicator_helper.resolve_aggregated(isovists, indicator=Indicator(code="pop"), moment=Moment(dow=DayOfWeek.monday, month=Month.february, hour=15))
# isovist_results:
#                                             geometry                                        destination  fov_deg  heading_deg  num_rays  radius_m  value
# 0  POLYGON ((-3.70587 40.42087, -3.70586 40.42088...  {'coordinates': [-3.70587, 40.42048], 'type': ...      360            0        -1       100    969
# 1  POLYGON ((-3.37825 40.47294, -3.37825 40.47295...  {'coordinates': [-3.37825, 40.47281], 'type': ...      360            0        -1       100     80

isoline_results = indicator_helper.resolve_aggregated(isolines, indicator=Indicator(code="pop"), moment=Moment(dow=DayOfWeek.monday, month=Month.february, hour=10))
# isoline_results:
#                                             geometry                                        destination        mode moment  range_s  value
# 0  POLYGON ((-3.70711 40.42145, -3.70668 40.42162...  {'coordinates': [-3.70587, 40.42048], 'type': ...  pedestrian   None      200  42034
# 1  POLYGON ((-3.37975 40.47380, -3.37967 40.47432...  {'coordinates': [-3.37825, 40.47281], 'type': ...  pedestrian   None      200   5784
```

You can see now the people count on the new `value` column of the dataframes.

Internally, Portall splits the areas of interest in [H3 cells]/https://eng.uber.com/h3/), obtains the people count for each cell and aggregates them. It is also possible to get the disaggregated results for each of the cells. In this case, only one input geometry can be used at a time:

```python
isovist_disaggregated_results = indicator_helper.resolve_disaggregated(isovists["geometry"][0], indicator=Indicator(code="pop", aggregated=False), moment=Moment(dow=DayOfWeek.monday, month=Month.february, hour=15))
# isovist_disaggregated_results:
#                                             geometry                  id       value  weight
# 0  POLYGON ((-3.70606 40.42066, -3.70618 40.42063...  631507574769340927  157.692308       1
# 1  POLYGON ((-3.70584 40.42064, -3.70596 40.42060...  631507574769341439  250.000000       1
# 2  POLYGON ((-3.70593 40.42080, -3.70604 40.42076...  631507574769343487  123.076923       1
# 3  POLYGON ((-3.70571 40.42077, -3.70583 40.42074...  631507574769495551  296.153846       1
# 4  POLYGON ((-3.70579 40.42094, -3.70591 40.42090...  631507574769510399  142.307692       1

isoline_disaggregated_results = indicator_helper.resolve_disaggregated(isolines["geometry"][0], indicator=Indicator(code="pop", aggregated=False), moment=Moment(dow=DayOfWeek.monday, month=Month.february, hour=15))
# isoline_disaggregated_results:
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

The resulting geodataframes are different now, and represent one [H3 cell](https://eng.uber.com/h3/) per row, with its geometry and id as columns, together with the `value` column itself and a `weight` column that can be useful if you want to aggregate the data from this disaggregated geodataframe yourself.

## Preflight

All those API requests incur in credit costs. To know about those costs in advance, you can create a preflight client and send the very same request beforehand. Preflight works for batch requests too.

```python
import pandas as pd

from pyportall.api.engine.core import APIClient
from pyportall.api.models.lbs import GeocodingOptions
from pyportall.api.engine.geopandas import GeocodingHelper
from pyportall.exceptions import PreFlightException


preflight_client = APIClient(api_key="MY_API_KEY", preflight=True)

addresses = pd.DataFrame({"street": ["Gran Vía 46", "Calle Alcalá 10"], "city": ["Madrid", "Madrid"]})
addresses

preflight_geocoding_helper = GeocodingHelper(preflight_client)

try:
    preflight_geocoding_helper.resolve(addresses, options=GeocodingOptions(country="Spain"))
except PreFlightException as e:
    geocoding_cost = e.credits
    # geocoding_cost: 2  (you may get a different value)
```

Now you can simple go ahead and execute the actual operation, knowing the number of credits that will be deducted from your account:

```python
client = APIClient(api_key="MY_API_KEY")

geocoding_helper = GeocodingHelper(client)

geocodings = geocoding_helper.resolve(addresses, options=GeocodingOptions(country="Spain"))

# geocodings:
#                     geometry country state county    city district postal_code           street
# 0  POINT (-3.70587 40.42048)   Spain  None   None  Madrid     None        None      gran via 46
# 1  POINT (-3.37825 40.47281)   Spain  None   None  Madrid     None        None  calle alcalá 10
```

## Metadata

You will need to look at the metadata catalog to learn about the different indicators that are available to you. Something like this:

```python
from pyportall.api.engine.core import APIClient
from pyportall.api.engine.metadata import MetadataHelper


client = APIClient(api_key="MY_API_KEY")

metadata_helper = MetadataHelper(client)

footfall = metadata_helper.all()[0]
# footfall: IndicatorMetadata(code='pop', name='Footfall', description='Number of people', unit='', format='', coverage='Madrid - UFA', resolution='H3 (11, 12)', data_source='Orange', computed_date=datetime.date(2019, 2, 1), aggregate_fn=<Aggregate.sum: 'sum'>, data_type=<DataType.integer: 'integer'>)
```
