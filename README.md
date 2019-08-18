# PyKbg

**PyKbg** is a Python wrapper around [Kelbongoo][]’s website.

[Kelbongoo]: https://www.kelbongoo.com

## Install

    pip3 install kbg

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

### `Kbg` methods
* `logged_in()` (`bool`): return a boolean indicating if the object is
  successfully connected. The `Kbg` constructor raises an exception on failed
  login.
* `get_customer_information()` (`dict`): get some information about the
  consumer, including first and last name, email, phone, email settings.
* `get_customer_orders(page=1)` (`dict`): get all the customer’s orders
  (paginated endpoint).
* `get_all_customer_orders()` (generator): yield all the customer’s orders.
  This is a useful wrapper around the previous method. If `full=True` is
  passed, call `get_customer_order` on each order to yield its full
  information. If all you want is the products’ full names, use
  ``get_store_offer_dicts`` as a lookup map to save unnecessary requests.
* `get_customer_order(order_id)` (`dict`): get more information about a
  specific order.

Additionnally, `Kbg` has all the endpoints `UnauthenticatedKbg` has.

### `UnauthenticatedKbg` methods
* `get_stores()` (`list` of `dict`s): get the list of stores (four at the
  moment).
* `get_store_availabilities(store_id)` (`dict`): get product availabilities at
  the given store.
* `get_store_offer(store_id)` (`dict`): get the offer at a the given store.
  This includes all products along with their producers, categories, and
  families (subcategories).
* `get_store_offer_dicts(store_id)` (`dict`): equivalent of `get_store_offer`
  that returns lookup ``dict``s rather than lists of items.

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
        product_id = product["producerproduct_id"]
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
