# What is pylex?

The pylex is a requests & session wrapper and handler for automating the tasks.


# Installation

`pip install pylexclient`


# Usage

## Importing 

`import * from pylex`

## Stdout

`Runtime.log('Hello World!', color='green')`


# Requirements
The pylex module relies on two major varibles:
* pref *(dict)*
* env *(dict)*

## env
```
env = {
        'production': False,  # bool | triggers sys.argv for pref and env
        '__key': '<elx_key>',
        'timezone': 'US/Eastern',
        'snipes_timezone': 'GMT',
        'errors': [],
        '__type': '4:VI|5:MC|3:AE|6:DI',
        'retries': {
            'some_func.name': 2,
            'some_other_func.name': 3,
            'and, so on': 5
        }, # or simply value can be 'infinite' if you want for all of the functions
        'retry_interval': 1, # time.sleep($1) for each retry attempt
        'mode': 'default',  # different for each site, used by you
        'release': int # Some UNIX timestamp for a particular release
    }
```

## pref
```
pref = {
        'site': 'https://www.<some_site>.com',
        'size': '10',
        'qty': '1',
        'proxy': "<host>:<port>:<username>:<password>", # a dict, or "<username>:<password>@<host>:<port>"
        'cloudflare': True, # Bypasses cloudflare
        'profile': {
            "profileID": int,
            "profileName": "Test",
            "firstName": "<value_required>",
            "lastName": "<value_required>",
            "phoneNumber": "<value_required>",
            "email": "<value_required>",
            "shippingAddress1": "<value_required>",
            "shippingAddress2": "<optional>",
            "zipcode": "<value_required>",
            "city": "<value_required>",
            "state": "<value_required>",
            "country": "<value_required>",
            "shippingSameBilling": "true",
            "cardFullName": "<value_required>",
            "cardType": "<value_required>",
            "cardNumber": "<value_required>",
            "cardCVC": "<value_required>",
            "cardExpirationMonth": "<value_required>",
            "cardExpirationYear": "<value_required>",
            'stateName': '<value_required>',
            'countryIso': '<value_required>'
        },
        'url': 'protocol://fqdn/uri?query',
        'webhook': {
            'private': '<value_required>',
            'public': '<value_required>',
            'admin': '<value_required>'
        }
    }
```


# Worker

## Declare *SomeSite*
Declare SomeSite and make sure to call `super().__init__(pref)`
```
class SomeSite(Instance):
    def __init__(self, pref):
        # App::Imports
        super().__init__(pref)
        if 'url' not in pref:
            self.errors.append('Invalid or empty URL in pref')
        if not self.is_valid():
            self.echo_errors()
            pass
```

## Blueprint
A blueprint is a dict of `func.__name__` as each attr with value include a dict of method to apply as a validator for each function in worker.
*The dummy blueprint dict:*
```
blueprint = {
    'variants': dict(key='success', matches=True, inverse=False, obj=False, json=True),
    'add_to_cart': dict(key='success', matches=True, inverse=False, obj=False, json=True),
    'opt_guest_checkout': dict(key='', obj=False, json=False),
    'verify_billing': dict(key='address', obj=True, json=True),
    'save_billing': dict(key='goto_section', matches='shipping_method', obj=False, json=True),
    'send_shipping_rates': dict(key='goto_section', matches='payment', obj=False, json=True),
    'add_card': dict(key='goto_section', matches='review', obj=False, json=True),
    'dig_paypal': dict(key='Location', headers=True),
    'send_payment': dict(key='', obj=False, json=False)  # No Check
}
```

## Initializing
```
some_site = SomeSite(pref)
workflow = [
    (some_site.variants, ('Getting product data', 'yellow'),),
    (some_site.add_to_cart, ('Adding to cart', 'yellow'),),
    (some_site.opt_guest_checkout, ('Opting for "Guest Checkout"', 'yellow'),),
    (some_site.verify_billing, ('Verifying Billing Data', 'light_magenta'),),
    (some_site.save_billing, ('Saving Billing Data', 'purple_1a'),),
    (some_site.send_shipping_rates, ('Sending Shipping Rates', 'hot_pink_3b'),),
    (some_site.add_card, ('Sending Credit Card Data', 'light_cyan'),) if 'paypal' not in pref or not pref['paypal']
    else (some_site.dig_paypal, ('Generating Paypal URL', 'light_cyan'), paypal_handler),
    (some_site.send_payment, ('Placing the Order', 'light_cyan'), order_handler),
]
if not len(some_site.errors) > 0:
    worker = Worker(env=env, main=some_site, workflow=workflow, blueprint=blueprint)
    worker.start()
```

## Warning

* *pylex* has no documentation or support & shall only be used by a group of developers for now.
