# PyKbg

**PyKbg** is a Python wrapper around [Kelbongoo][]’s website.

[Kelbongoo]: https://www.kelbongoo.com

Kelbongoo is a [social economy][] company operating in the East of Paris,
France. It sells products from small local producers (mostly located in the
[Picardy][]), and is the only intermediary between the producer and the
consumer ([short food supply chain][sfsc]).

[Picardy]: https://en.wikipedia.org/wiki/Picardy
[sfsc]: https://en.wikipedia.org/wiki/Short_food_supply_chains
[social economy]: https://en.wikipedia.org/wiki/Social_economy

* [Install](#install)
* [Usage](#usage)
* [API Docs](#api-docs)
* [Examples](#examples)
* [Compatibility](#compatibility)
* [Notes](#notes)

## Install

```shell
pip3 install kbg
```

This requires Python ≥3.5.

## Usage
Use the `Kbg` class to initiate a connection:
```python3
from kbg import Kbg

k = Kbg(your_email, your_password)
print(k.logged_in()) # True
```

Some general endpoints are available without connection:
```python3
from kbg import UnauthenticatedKbg

k = UnauthenticatedKbg()
print(k.logged_in()) # False
```

## API Docs

### `Kbg`
The `Kbg` constructor takes an email and a password. It raises an exception on
failed login.

`Kbg` has all the endpoints `UnauthenticatedKbg` has, plus the following ones:

#### `logged_in()`
Return a boolean indicating if the object is successfully connected.

#### `get_customer_information()`
Get some information as a `dict` about the consumer, including first and last
name, email, phone, email settings.

#### `get_customer_orders(page=1)`
Get all the customer’s orders. This is a paginated endpoint. It returns a `dict` with an `orders` key as well as a `count`, `page` and `next_page` ones that you can use to get the next pages, if any.

#### `get_all_customer_orders(full=False)`
Yield all the customer’s orders. This is a useful wrapper around
`get_customer_order`.

If `full=True` is passed, call `get_customer_order` on each order to yield its
full information.

Note that if all you want is the products’ full names, use
`get_store_offer_dicts` as a lookup map instead of `full=True` to save
unnecessary requests.

#### `get_customer_order(order_id)`
Get more information about a specific order (`dict`).

### `UnauthenticatedKbg`
The `UnauthenticatedKbg` constructor doesn’t take any argument.

#### `get_stores()`
Get the list of stores (`list` of `dict`s).

#### `get_store_availabilities(store_id)`
Get product availabilities at the given store for the current command window,
as a map of product ids to units count.

#### `get_store_offer(store_id, force=False)`
Get the offer at a the given store (`dict`). This includes all products along
with their producers, categories, and families (subcategories).

Note this method is cached; use `force=True` to force the API call.

#### `get_store_offer_dicts(store_id, force=False)`
Equivalent of `get_store_offer` that returns lookup `dict`s rather than lists
of items.

#### `get_store_status(store_id)`
Return a `dict` describing a store’s status.

* `is_active` (`bool`): is the store active, i.e. are we in the timeframe for
    orders?
* `is_full` (`bool`): is the store full, i.e. it can’t take anymore orders?
* `full_tags` (`str` `list`): what is full? Possible values: `"ORDERS"`, `"SEC"`, `"FRAIS"`

### Examples
Create a simple connection:
```python3
from kbg import Kbg

k = Kbg("your@email.com", "yourpassword")
```

#### Compute your total spending
```python3
total_spent = 0

for order in k.get_all_customer_orders():
    for product in order["products"]:
        total_spent += product["consumer_price"]

# get a price in euros rather than cents
total_spent /= 100

print("You spent a total of %.2f€ at Kelbongoo!" % total_spent)
```

#### Print your most-bought products
```python3
from collections import Counter

my_store = "BOR"

top_products = Counter()
top_producers = Counter()
store_products = k.get_store_offer_dicts(my_store)["products"]

for order in k.get_all_customer_orders():
    for product in order["products"]:
        product_id = product["id"]
        if product_id in store_products:
            product = store_products[product_id]
            top_products[product["product_name"]] += 1
            top_producers[product["producer_name"]] += 1

print("Top products:")
for product, n in top_products.most_common(5):
    print("%3d - %s" % (n, product))

print("\nTop producers:")
for producer, n in top_producers.most_common(5):
    print("%3d - %s" % (n, producer))
```

#### Find your beers coverage
```python3
my_store = "BOR"

offer = k.get_store_offer(my_store)

# Get the id of the family 'Bières' ("Beers")
beer_family_id = None
for family in offer["families"]:
    if family["name"] == "Bières":
        beer_family_id = family["id"]
        break
else:
    raise Exception("Can't find the beer family! :(")

# Collect all products in that family
beers = {}
for product in offer["products"]:
    if product["family_id"] == beer_family_id:
        beers[product["id"]] = "%-40s (%s)" % (
                product["product_name"], product["producer_name"])

known_beers = set()

# Collect all *bought* products in that family
for order in k.get_all_customer_orders():
    for product in order["products"]:
        product_id = product["id"]
        if product_id in beers:
            known_beers.add(product_id)

print("You have tasted %d beers out of %d." % (len(known_beers), len(beers)))
if len(known_beers) != len(beers):
    print("Other beers you might want to try:")
    for beer_id, beer in beers.items():
        if beer_id not in known_beers:
            print("*", beer)
```

## Compatibility
This library uses undocumented API endpoints, so it may break at any time.

## Notes
Don’t confuse KBG (Kelbongoo) with [KGB](https://en.wikipedia.org/wiki/KGB).

The Kelbongoo API refers to stores as “locales”, using the first tree letters
in upper-case as a primary key: `BOR` is Borrégo and `BIC` is Bichat, for
example.

Prices are given in €uro cents; you need to divide them by 100 to get the
price in €uro: `"consumer_price": 221` means it’s something that costs €2.21.

Please throttle your requests to respect Kelbongoo’s servers.
