# pyportall

Python SDK to Portall

## Installation

Installing is straightforward:

```
$ pip install -e git+git@github.com:inspide/pyportall.git@0.0.1#egg=pyportall
```

Or, as part of your `requirements.txt` file:

```
...
-e git+git@github.com:inspide/pyportall.git@0.0.1#egg=pyportall
...
```

If you want to use GeoPandas with this SDK, you need to install it separately as it will not be automatically installed by default.

## Authentication

Your must use the `API_KEY` environment variable to store your API key to Portall for the Python SDK to work.

## Regular Python usage example

We will show how to find the footfall value for an isoline and an isovist in 3 different hours of a Friday in February.

First of all, let us find out about the available indicators, and make sure footfall is there:

```python
from pyportall.metadata import MetadataHelper


metadata_helper = MetadataHelper()

indicators = metadata_helper.all()
# indicators: [IndicatorMetadata(code='pop', name='Footfall', description='Number of people', unit='', format='', coverage='Madrid - UFA', resolution='H3 (11, 12)', data_source='Orange', computed_date=datetime.date(2019, 2, 1), aggregate_fn=<Aggregate.sum: 'sum'>, data_type=<DataType.integer: 'integer'>), IndicatorMetadata(code='avg_stay_total', name='Total stay time', description='Accumulated time spent in this area', unit='', format='', coverage='', resolution='', data_source='Inspide', computed_date=datetime.date(2020, 10, 14), aggregate_fn=<Aggregate.avg: 'avg'>, data_type=<DataType.decimal: 'decimal'>)]
```

`indicators` now holds a list on `Indicator` objects. `location`, `moment` and `value` are `None` because the indicator has not been calculated yet. More on that later.

Now let us find the isoline and isovist we want to use:

```python
from pyportall.models import Options, Position, Isoline, IsolineMode, Isovist, Indicator
from pyportall.engine import GeocodingHelper, IsolineHelper, IsovistHelper, IndicatorHelper
from pyportall.api import APIClient


client = APIClient(api_key="MY_API_KEY")  # API key can also be automatically detected from the API_KEY enviroment variable; a batch boolean is also available (defaults to False) to avoid timeouts


geocoding_helper = GeocodingHelper(client, options=Options(country="Spain"))

gran_via_40 = Position(address="Gran vía 40 Madrid")
# gran_via_40: Position(lon=None, lat=None, address='Gran vía 40 Madrid')

paseo_castellana_80 = Position(address="Paseo de la Castellana 80 Madrid")
# paseo_castellana_80: Position(lon=None, lat=None, address='Paseo de la Castellana 80 Madrid')

geocoding_helper.resolve([gran_via_40, paseo_castellana_80])
# gran_via_40: Position(lon=-3.70499, lat=40.42041, address='Gran vía 40 Madrid')
# paseo_castellana_80: Position(lon=-3.69111, lat=40.44177, address='Paseo de la Castellana 80 Madrid')

isoline_helper = IsolineHelper(client)

isoline = Isoline(destination=gran_via_40, mode=IsolineMode("car"), range_s=300)
# isoline: Isoline(id=None, destination=Position(lon=-3.70499, lat=40.42041, address='Gran vía 40 Madrid'), mode=<IsolineMode.car: 'car'>, range_s=300, moment=None, geom=None)

isoline_helper.resolve([isoline])
# isoline: Isoline(id=None, destination=Position(lon=-3.70499, lat=40.42041, address='Gran vía 40 Madrid'), mode=<IsolineMode.car: 'car'>, range_s=300, moment=None, geom=Polygon(coordinates=[[(-3.7180996, 40.4207611), ..., (-3.7180996, 40.4207611)]], type='Polygon'))

isovist_helper = IsovistHelper(client)

isovist = Isovist(destination=paseo_castellana_80)
# isovist: Isovist(id=None, destination=Position(lon=-3.69111, lat=40.44177, address='Paseo de la Castellana 80 Madrid'), radius_m=150, num_rays=-1, heading_deg=0, fov_deg=360, geom=None)

isovist_helper.resolve([isovist])
# isovist: Isovist(id=None, destination=Position(lon=-3.69111, lat=40.44177, address='Paseo de la Castellana 80 Madrid'), radius_m=150, num_rays=-1, heading_deg=0, fov_deg=360, geom=Polygon(coordinates=[[(-3.69111, 40.44312031), ..., (-3.69111, 40.44312031)]], type='Polygon'))
```

Next step is to define the time frame we want to use:

```python
from pyportall.models import Moment


moments = [Moment(dow="friday", month="february", hour=10), Moment(dow="friday", month="february", hour=18)]
# moments: Moment(id=None, dow=<DayOfWeek.friday: 'friday'>, month=<Month.february: 'february'>, hour=10, year=2020), Moment(id=None, dow=<DayOfWeek.friday: 'friday'>, month=<Month.february: 'february'>, hour=18, year=2020)]
```

We are now ready to make the calculations:

```python
footfall = Indicator(code=indicators[0].code)

indicator_helper = IndicatorHelper(client)

final_indicators = indicator_helper.resolve([footfall], [isovist, isoline], moments)
# final_indicators: [Indicator(code='pop', normalization=<Normalization.total: 'total'>, location='0', moment='0', value=1524), Indicator(code='pop', normalization=<Normalization.total: 'total'>, location='0', moment='1', value=810), Indicator(code='pop', normalization=<Normalization.total: 'total'>, location='1', moment='0', value=269669),  Indicator(code='pop', normalization=<Normalization.total: 'total'>, location='1', moment='1', value=350762)]
```

`final_indicators` hold 4 indicators, one for each isovist/isoline and moment combination. It is possible to match the values with the corresponding combination by looking at the `location` and `moment` fields. Those two fields include now an `id` that can be found in the respective isovist/isoline or moment:

```python
# isoline: Isoline(id='1', destination=Position(lon=-3.70499, lat=40.42041, address='Gran vía 40 Madrid'), mode=<IsolineMode.car: 'car'>, range_s=300, moment=None, geom=Polygon(coordinates=[[(-3.7180996, 40.4207611), ..., (-3.7180996, 40.4207611)]], type='Polygon'))

# isovist: Isovist(id='0', destination=Position(lon=-3.69111, lat=40.44177, address='Paseo de la Castellana 80 Madrid'), radius_m=150, num_rays=-1, heading_deg=0, fov_deg=360, geom=Polygon(coordinates=[[(-3.69111, 40.44312031), ..., (-3.69111, 40.44312031)]], type='Polygon'))

# moments: Moment(id='0', dow=<DayOfWeek.friday: 'friday'>, month=<Month.february: 'february'>, hour=10, year=2020), Moment(id='1', dow=<DayOfWeek.friday: 'friday'>, month=<Month.february: 'february'>, hour=18, year=2020)]
```

If any isoline, isovist or moment had had any previous `id`, it would have been respected.

## Geopandas usage example

A similar result could have been achived using Geopandas. We will use one isovists instead of one isovist and one isoline for simplicity's sake. By the way, regular polygons could also be used both here and in the previous example directly.

```python
import pandas as pd
import geopandas as gpd

from pyportall.models import Options
from pyportall.geopandas import GeocodingHelper, IsovistHelper, IndicatorHelper, combine
from pyportall.api import APIClient


client = APIClient(api_key="MY_API_KEY")  # API key can also be automatically detected from the API_KEY enviroment variable; a batch boolean is also available (defaults to False) to avoid timeouts


addresses = pd.Series(["Gran vía 40 Madrid", "Paseo de la Castellana 80 Madrid"])
# addresses:
# 0                  Gran vía 40 Madrid
# 1    Paseo de la Castellana 80 Madrid

geocoding_helper = GeocodingHelper(client, options=Options(country="Spain"))

points = geocoding_helper.from_series(addresses)
# points:
# 0    POINT (-3.70499 40.42041)
# 1    POINT (-3.69111 40.44177)

isovist_helper = IsovistHelper(client)

isovists = isovist_helper.from_gdf(gpd.GeoDataFrame({"geometry": points}, crs="EPSG:4326"))
# isovists:
#                                             geometry
# 0  POLYGON ((-3.70499 40.42096, -3.70498 40.42095...
# 1  POLYGON ((-3.69111 40.44312, -3.69108 40.44312...

moments = pd.DataFrame({"month": ["february", "february"], "dow": ["friday", "friday"], "hour": [6, 23]})
# moments:
#       month     dow  hour
# 0  february  friday     6
# 1  february  friday    23

time_and_space = combine(isovists, moments)
time_and_space["indicator"] = "pop"
# time_and_space:
#                                             geometry  tmp     month     dow  hour indicator
# 0  POLYGON ((-3.70499 40.42096, -3.70498 40.42095...    1  february  friday     6  pop
# 1  POLYGON ((-3.70499 40.42096, -3.70498 40.42095...    1  february  friday    23  pop
# 2  POLYGON ((-3.69111 40.44312, -3.69108 40.44312...    1  february  friday     6  pop
# 3  POLYGON ((-3.69111 40.44312, -3.69108 40.44312...    1  february  friday    23  pop

indicator_helper = IndicatorHelper(client)

result = indicator_helper.from_gdf(time_and_space)
# result:
#                                             geometry  tmp     month     dow  hour indicator  value
# 0  POLYGON ((-3.70499 40.42096, -3.70498 40.42095...    1  february  friday     6  pop    116
# 1  POLYGON ((-3.70499 40.42096, -3.70498 40.42095...    1  february  friday    23  pop   1584
# 2  POLYGON ((-3.69111 40.44312, -3.69108 40.44312...    1  february  friday     6  pop    569
# 3  POLYGON ((-3.69111 40.44312, -3.69108 40.44312...    1  february  friday    23  pop    942
```

## Geopandas usage example (take 2)

You can still use the regular Python objects to work with Geopandas and get the best of the two worls:

```python
from pyportall.models import Options, Position, Isovist, Moment
from pyportall.geopandas import GeocodingHelper, IsovistHelper, IndicatorHelper, combine, to_df, to_gdf
from pyportall.metadata import MetadataHelper
from pyportall.api import APIClient


client = APIClient(api_key="MY_API_KEY")  # API key can also be automatically detected from the API_KEY enviroment variable; a batch boolean is also available (defaults to False) to avoid timeouts


geocoding_helper = GeocodingHelper(client, options=Options(country="Spain"))

positions = [Position(address="Gran vía 40 Madrid"), Position(address="Paseo de la Castellana 80 Madrid")]
# positions: [Position(lon=None, lat=None, address='Gran vía 40 Madrid'), Position(lon=None, lat=None, address='Paseo de la Castellana 80 Madrid')]

geocoding_helper.resolve(positions)
# positions: [Position(lon=-3.70499, lat=40.42041, address='Gran vía 40 Madrid'), Position(lon=-3.69111, lat=40.44177, address='Paseo de la Castellana 80 Madrid')]

isovist_helper = IsovistHelper(client)

isovists = [Isovist(destination=position) for position in positions]
# isovists: [Isovist(id=None, destination=Position(lon=-3.70499, lat=40.42041, address='Gran vía 40 Madrid'), radius_m=150, num_rays=-1, heading_deg=0, fov_deg=360, geom=None), Isovist(id=None, destination=Position(lon=-3.69111, lat=40.44177, address='Paseo de la Castellana 80 Madrid'), radius_m=150, num_rays=-1, heading_deg=0, fov_deg=360, geom=None)]

isovist_helper.resolve(isovists)
# isovists: [Isovist(id=None, destination=Position(lon=-3.70499, lat=40.42041, address='Gran vía 40 Madrid'), radius_m=150, num_rays=-1, heading_deg=0, fov_deg=360, geom=Polygon(coordinates=[[(-3.70499, 40.420957996), ..., (-3.70499, 40.420957996)]], type='Polygon')), Isovist(id=None, destination=Position(lon=-3.69111, lat=40.44177, address='Paseo de la Castellana 80 Madrid'), radius_m=150, num_rays=-1, heading_deg=0, fov_deg=360, geom=Polygon(coordinates=[[(-3.69111, 40.44312031), ..., (-3.69111, 40.44312031)]], type='Polygon'))]

moments = [Moment(dow="friday", month="february", hour=10), Moment(dow="friday", month="february", hour=18)]
# moments: Moment(id=None, dow=<DayOfWeek.friday: 'friday'>, month=<Month.february: 'february'>, hour=10, year=2020), Moment(id=None, dow=<DayOfWeek.friday: 'friday'>, month=<Month.february: 'february'>, hour=18, year=2020)]

metadata_helper = MetadataHelper()

footfall = metadata_helper.all()[0]
# footfall: IndicatorMetadata(code='pop', name='Footfall', description='Number of people', unit='', format='', coverage='Madrid - UFA', resolution='H3 (11, 12)', data_source='Orange', computed_date=datetime.date(2019, 2, 1), aggregate_fn=<Aggregate.sum: 'sum'>, data_type=<DataType.integer: 'integer'>)

time_and_space = combine(to_gdf(isovists), to_df(moments))
# time_and_space:
#    id_x                                        destination  radius_m  num_rays  heading_deg  fov_deg  ... tmp  id_y     dow     month hour  year
# 0  None  {'lon': -3.70499, 'lat': 40.42041, 'address': ...       150        -1            0      360  ...   1  None  friday  february   10  2020
# 1  None  {'lon': -3.70499, 'lat': 40.42041, 'address': ...       150        -1            0      360  ...   1  None  friday  february   18  2020
# 2  None  {'lon': -3.69111, 'lat': 40.44177, 'address': ...       150        -1            0      360  ...   1  None  friday  february   10  2020
# 3  None  {'lon': -3.69111, 'lat': 40.44177, 'address': ...       150        -1            0      360  ...   1  None  friday  february   18  2020

# [4 rows x 13 columns]

time_and_space["indicator"] = footfall.code
# time_and_space:
#    id_x                                        destination  radius_m  num_rays  heading_deg  fov_deg  ...  id_y     dow     month hour  year  indicator
# 0  None  {'lon': -3.70499, 'lat': 40.42041, 'address': ...       150        -1            0      360  ...  None  friday  february   10  2020   pop
# 1  None  {'lon': -3.70499, 'lat': 40.42041, 'address': ...       150        -1            0      360  ...  None  friday  february   18  2020   pop
# 2  None  {'lon': -3.69111, 'lat': 40.44177, 'address': ...       150        -1            0      360  ...  None  friday  february   10  2020   pop
# 3  None  {'lon': -3.69111, 'lat': 40.44177, 'address': ...       150        -1            0      360  ...  None  friday  february   18  2020   pop

# [4 rows x 14 columns]

indicator_helper = IndicatorHelper(client)

result = indicator_helper.from_gdf(time_and_space)
# result:
#    id_x                                        destination  radius_m  num_rays  heading_deg  fov_deg  ...     dow     month hour  year indicator  value
# 0  None  {'lon': -3.70499, 'lat': 40.42041, 'address': ...       150        -1            0      360  ...  friday  february   10  2020  pop   1205
# 1  None  {'lon': -3.70499, 'lat': 40.42041, 'address': ...       150        -1            0      360  ...  friday  february   18  2020  pop   2444
# 2  None  {'lon': -3.69111, 'lat': 40.44177, 'address': ...       150        -1            0      360  ...  friday  february   10  2020  pop   3490
# 3  None  {'lon': -3.69111, 'lat': 40.44177, 'address': ...       150        -1            0      360  ...  friday  february   18  2020  pop   2275

# [4 rows x 15 columns]
```

It may seem a bit less direct than the previous example, but using the models you get all sorts of validation and interesting helper functions.
