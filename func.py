# -*- coding: utf-8 -*-
"""func.py
This file holds the main routine that will be executed by the function.

"""
from enum import Enum
import requests
import pymongo
from datetime import datetime
import pytz

from utils import get_runtime_variables


secrets = get_runtime_variables()
collection: pymongo.collection = None


class QuoteType(Enum):
    First = 1,
    Up = 2,
    Down = 3


def __get_mongo_collection__() -> pymongo.collection:
    global collection

    if collection is not None:
        return collection

    mongo_conn_string = "mongodb+srv://{mongo_user}:{mongo_pass}@cluster0.y7r7m.mongodb.net/?retryWrites=true&w=majority".format(
        mongo_user=secrets["mongo_user"],
        mongo_pass=secrets["mongo_pass"]
    )

    client = pymongo.MongoClient(mongo_conn_string)
    db = client[secrets["mongo_database"]]
    collection = db["currency"]

    return collection


def _get_last_fetched_():
    col = __get_mongo_collection__()
    latest = col.find_one({}, sort=[('_id', pymongo.DESCENDING)])
    return latest


def _add_quote_(quote: dict):
    col = __get_mongo_collection__()
    col.insert_one(quote)


def _get_quote_():
    url = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_currency}&to_currency={to_currency}&apikey={alpha_vantage_key}".format(
        alpha_vantage_key=secrets["alpha_vantage_key"],
        from_currency=secrets["from_currency"],
        to_currency=secrets["to_currency"]
    )
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError(f"Failed to get quote. Received status {r.status_code}: {r.reason}")

    data = r.json()["Realtime Currency Exchange Rate"]

    dt = datetime.strptime(data["6. Last Refreshed"], "%Y-%m-%d %H:%M:%S")
    utc_dt = dt.astimezone(pytz.utc)

    return {
        "fetchedAt": datetime.utcnow(),
        "refreshedAt": utc_dt,
        "value": float(data["5. Exchange Rate"])
    }


def notify(quote: dict, quote_type: QuoteType):
    if quote_type == QuoteType.First:
        message = f"First quote fetched @ {quote['fetchedAt']}! "

    elif quote_type == QuoteType.Up:
        message = f"Oh no! CAD price just went up @ {quote['fetchedAt']}! "

    else:
        message = f"Oh yeah! CAD price just wen down @ {quote['fetchedAt']}! "

    message = f"{message}" \
              f"Current value: {quote['value']}. " \
              f"It was last updated at: {quote['refreshedAt']}"

    url = "https://api.telegram.org/bot{bot_key}/sendMessage?chat_id={chat_id}&text={message}".format(
        bot_key=secrets["telegram_bot_key"],
        chat_id=secrets["telegram_chat_id"],
        message=message
    )

    r = requests.get(url)
    if r.status_code < 200 or r.status_code > 299:
        raise ValueError(f"Failed to send notification message. Got status {r.status_code} - {r.reason}")


def check_quote():
    latest_quote = _get_last_fetched_()
    quote = _get_quote_()

    if latest_quote is None:
        _add_quote_(quote)
        notify(quote, QuoteType.First)
        return

    threshold = secrets["threshold"]
    last_value = latest_quote["value"]
    new_value = quote["value"]
    diff = last_value * threshold

    if new_value <= (last_value - diff):
        # Send a notification if the value goes bellow the threshold.
        notify(quote, QuoteType.Down)

    elif new_value >= (last_value + diff):
        # Send a notification if the value goes above the threshold.
        notify(quote, QuoteType.Up)

    else:
        # If the new value is within the threshold, I won't update the database (because if I do, there will never be
        # a value outside the threshold).
        return

    _add_quote_(quote)


if __name__ == '__main__':
    check_quote()
