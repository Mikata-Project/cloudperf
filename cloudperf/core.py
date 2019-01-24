from __future__ import absolute_import
import importlib
import pkgutil
import cloudperf.providers
import cachetools
import pandas as pd


@cachetools.cached(cache={})
def get_providers():
    prov_path = cloudperf.providers.__path__
    providers = []

    for _, name, _ in pkgutil.iter_modules(prov_path):
        m = importlib.import_module(name='.{}'.format(name), package='cloudperf.providers')
        if getattr(m, 'CloudProvider', None):
            providers.append(m.CloudProvider())
    return providers


@cachetools.cached(cache={})
def get_prices(prices=None, update=False):
    # if we got a stored file and update is True, merge the two by overwriting
    # old data with new (and leaving not updated old data intact)
    if prices and update:
        try:
            old = pd.read_json(prices, orient='records')
            new = pd.concat([cp.get_prices() for cp in get_providers()], ignore_index=True, sort=False)
            return new.combine_first(old)
        except Exception:
            pass
    if prices:
        try:
            return pd.read_json(prices, orient='records')
        except Exception:
            pass
    return pd.concat([cp.get_prices() for cp in get_providers()], ignore_index=True, sort=False)


def get_performance(prices=None, perf=None, update=False, expire=False):
    # if we got a stored file and update is True, merge the two by overwriting
    # old data with new (and leaving not updated old data intact).
    # if expire is set only update old data if the expiry period is passed
    if perf and update:
        old = pd.read_json(perf, orient='records')
        new = pd.concat([cp.get_performance(get_prices(prices), old, update, expire) for cp in get_providers()],
                        ignore_index=True, sort=False)
        return new.combine_first(old)
    if perf:
        try:
            return pd.read_json(perf, orient='records')
        except Exception:
            pass
    return pd.concat([cp.get_performance(get_prices(prices)) for cp in get_providers()], ignore_index=True, sort=False)


def get_perfprice(prices=None, perf=None):
    return price_df.merge(perf_df, on='instanceType')
