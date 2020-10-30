from pylex import *


class SomeSite(Instance):
    def __init__(self, pref):
        # App::Imports
        super().__init__(pref)
        if not self.is_valid():
            self.echo_errors()
            pass


# App::MiddleWares


###

def middleware(main, res):
    success, response = res
    return success

###


if __name__ == '__main__':

    def checkStatus():
        response = requests.get("<status_site>").text
        return response

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
        },  # or simply value can be 'infinite' if you want for all of the functions
        'retry_interval': 1,  # time.sleep($1) for each retry attempt
        'mode': 'default',  # different for each site, used by you
        'release': int  # Some UNIX timestamp for a particular release
    }

    pref = {
        'site': 'https://www.<some_site>.com',
        'size': '10',
        'qty': '1',
        'proxy': "<host>:<port>:<username>:<password>",  # a dict, or "<username>:<password>@<host>:<port>"
        'cloudflare': True,  # Bypasses cloudflare
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
            "billingFirstName": "<value_required>",
            "billingLastName": "<value_required>",
            "billingPhoneNumber": "<value_required>",
            "billingEmail": "<value_required>",
            "billingAddress1": "<value_required>",
            "billingAddress2": "<optional>",
            "billingZipcode": "<value_required>",
            "billingCity": "<value_required>",
            "billingState": "<value_required>",
            "billingCountry": "<value_required>",
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

    # Worker Section

    blueprint = {
        '<func_name>': dict(key='success', matches=True, inverse=False, obj=False, json=True),
    }

    # ENV :: production | sandbox

    mode = 'production'.upper() if env['production'] else 'default'.upper()
    if not mode == 'production'.upper():
        Runtime.production = True
        Runtime.log(f"Mode: {mode}", color='green')

    if env['production']:
        try:
            pref = json.loads(unquote(sys.argv[1]))
            env = json.loads(unquote(sys.argv[2]))
        except Exception as exp:
            env['errors'].append(str(exp))
            Runtime.log(
                'IMPORT_ERROR: invalid arguments provided.\n'
                'Default: $ {python interpreter} this.py {pref} {env}\n'
                'Arguments Data Format: JSON dumped & urlencoded\n'
                f"Raised: {str(exp)}",
                color='red'
            )
            pref = env = {}

    # Retries
    if 'retries' in env and env['retries'] == 'infinite':
        env['retries'] = {k: 10 ** 10 for k, v in blueprint.items()}
    if 'webhook' in pref and not pref['webhook'] == '':
        change_webhook(pref['webhook'])

    url = pref['url'] if 'url' in pref else ''
    if checkStatus() == '1':
        some_site = SomeSite(pref)
        workflow = [
            (some_site.some_func, ('Placing the Order', 'light_cyan'), order_handler),
        ]
        if not len(some_site.errors) > 0:
            worker = Worker(env=env, main=some_site, workflow=workflow, blueprint=blueprint)
            worker.start()
    else:
        Runtime.log('Site disabled', color='red')
