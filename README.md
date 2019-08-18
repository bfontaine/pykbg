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
* `get_consumer_information()` (`dict`): get some information about the consumer,
  including first and last name, email, phone, email settings.

Additionnally, `Kbg` has all the endpoints `UnauthenticatedKbg` has.

### `UnauthenticatedKbg` methods
* `get_stores()` (`list` of `dict`s): get the list of stores (four at the
  moment).
* `get_store_availabilities(store_id)` (`dict`): get product availabilities at
  the given store.
* `get_store_offer(store_id)` (`dict`): get the offer at a the given store.
  This includes all products along with their producers, categories, and
  families (subcategories).

## Compatibility

This library uses undocumented API endpoints, so it may break at any time.

## Naming

Don’t confuse KBG (Kelbongoo) with [KGB](https://en.wikipedia.org/wiki/KGB).

Note that the Kelbongoo API refers to stores as “locales”, using the first tree
letters in upper-case as a primary key: `BOR` is Borrégo and `BIC` is Bichat,
for example.
