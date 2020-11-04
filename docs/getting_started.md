# Getting started

## Installation

Installing is straightforward:

```
$ pip install pyportall
```

Or, as part of your `requirements.txt` file:

```
...
pyportall
...
```

Currently, GeoPandas is required for this SDK to work. We may release a standalone SDK version in the future.

### Tests

You may want to verify the installation is correct by running the test suite. Just run `pytest` if you want to run the tests against a mocked API:

```
$ pytest
```

You can also run the test suite against the live API if you use a real API key:

```
$ env PYPORTALL_API_KEY=MY_API_KEY pytest
```

## Authentication

Your can use the `API_KEY` environment variable to store your API key to Portall for the Python SDK to work, or pass it to [APIClient][pyportall.api.engine.core.APIClient] when instantiating the API client, as described in the next section.

## Restrictions

You may get `429` "too many requests" error if you run above the maximum number of requests per second set by your plan.

On a similar fashion, API calls cost credits. If you run out of credits, you will start receiving `429` error messages too.
