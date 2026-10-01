"""Custom prices (config model.prices), from notebook 05 section 0 (set_price / show_price).

Pydantic AI prices every model call from the genai-prices table: it looks the model up by the endpoint URL first,
then by the provider name. apply_custom_prices() puts the config's rates into a copy of that table, so everything
downstream uses them: the cost of each step, the stored cost_usd, limits.cost_limit, conv_cost_limit.
A rate left null keeps the table's own rate. A model the table does not know (a local model, a new one) gets a
new entry holding only the rates given: without a cache rate, cached input is billed at the input rate; without
an input or output rate, that part costs nothing.
Built-in rates can be tiered (Luna on Bedrock doubles above 272k tokens in one call); a custom rate is flat.

The table ships inside the genai-prices package. start_price_updates() (config model.update_prices) downloads the
latest one at startup and every hour after, and puts the config's rates back into each fresh table.
"""
import copy
from decimal import Decimal

import genai_prices.data_snapshot as ds
from genai_prices import UpdatePrices
from genai_prices.types import ClauseEquals, ModelInfo, ModelPrice

from .. import config

RATES = {"input": "input_mtok", "cache_read": "cache_read_mtok", "cache_write": "cache_write_mtok", "output": "output_mtok"}


def find_entry(snapshot, provider_name):
    """The price entry Pydantic AI uses for the configured model: by endpoint URL first, then by provider name.
    None when the table does not know the model."""
    for provider_id, url in ((None, config.BASE_URL), (provider_name, None)):
        try:
            return snapshot.find_provider_model(config.MODEL_ID, None, provider_id, url)[1]
        except LookupError:
            continue
    return None


def latest(prices):
    """An entry's prices are one ModelPrice, or a list of date-conditional ones: the last is the one in force."""
    return prices[-1].prices if isinstance(prices, list) else prices


def put_custom_prices(snapshot, provider_name):
    """Put the non-null rates of config model.prices into this price table (changed in place)."""
    custom = {RATES[name]: Decimal(str(value)) for name, value in config.PRICES.items() if value is not None}
    if not custom:
        return
    entry = find_entry(snapshot, provider_name)
    if entry is not None:
        old = latest(entry.prices)
        rates = {field: getattr(old, field, None) for field in RATES.values()}     # the table's rates ...
        rates.update(custom)                                                        # ... with the config's on top
        entry.prices = ModelPrice(**rates)
    else:
        providers = [p for p in snapshot.providers if p.id == provider_name]
        if not providers:
            print(f"custom prices not applied: the price table has no provider '{provider_name}'")
            return
        providers[0].models.insert(0, ModelInfo(id=config.MODEL_ID, match=ClauseEquals(equals=config.MODEL_ID),
                                                prices=ModelPrice(**custom)))


def apply_custom_prices(provider_name):
    """Put the non-null rates of config model.prices into the price table of this Python process."""
    if not any(value is not None for value in config.PRICES.values()):
        return
    snapshot = copy.deepcopy(ds.get_snapshot())
    put_custom_prices(snapshot, provider_name)
    ds.set_custom_snapshot(ds.DataSnapshot(providers=snapshot.providers, from_auto_update=False))


class UpdateWithCustomPrices(UpdatePrices):
    """The background download of the price table, with the config's rates put back into every fresh table."""
    provider_name = None

    def fetch(self):
        snapshot = super().fetch()
        if snapshot is not None:
            put_custom_prices(snapshot, self.provider_name)
        return snapshot


def start_price_updates(provider_name):
    """Download the latest genai-prices table now and again every hour (config model.update_prices), so a price
    change or a new model is picked up without upgrading the package. Waits up to 5 seconds for the first
    download; when it fails (no network), the installed table stays in use and the next try is an hour later.
    Costs already stored are never re-priced."""
    if not config.UPDATE_PRICES:
        return
    updater = UpdateWithCustomPrices()
    updater.provider_name = provider_name
    updater.start()
    try:
        if not updater.wait(5):
            print("price table: download not finished yet, the installed table is used until it is")
    except Exception as e:
        print(f"price table: download failed ({type(e).__name__}), the installed table is used")


def rates_line(provider_name):
    """One line for the terminal: the rates in force, USD per million tokens."""
    entry = find_entry(ds.get_snapshot(), provider_name)
    if entry is None:
        return "prices: none known for this model, cost shows n/a (set model.prices in the config)"
    prices = latest(entry.prices)
    parts = []
    for name, field in RATES.items():
        rate = getattr(prices, field, None)
        rate = getattr(rate, "base", rate)                         # tiered price: its base rate
        mark = " (custom)" if config.PRICES.get(name) is not None else ""
        missing = "same as input" if name.startswith("cache") else "0"
        parts.append(f"{name.replace('_', ' ')} {rate if rate is not None else missing}{mark}")
    return "prices, USD per M tokens: " + " | ".join(parts)
