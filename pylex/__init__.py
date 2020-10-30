#!/usr/bin/python3


#  /app/filestorage.py


import os
import json

fs_env = dict(errors=[])


class Importer:
    @staticmethod
    def get(mod_file):
        file_path = os.path.realpath(mod_file)
        if not os.path.isfile(file_path):
            return False
        with open(file_path, 'r') as mod_raw:
            return mod_raw.read()

    @staticmethod
    def json(mod_file):
        file_path = os.path.realpath(mod_file)
        if not os.path.isfile(file_path):
            return False
        with open(file_path, 'r') as mod_raw:
            try:
                mod = json.load(mod_raw)
            except json.JSONDecodeError:
                mod = mod_raw
            return mod


class Exporter:
    @staticmethod
    def set(file_path, data):
        file_path = os.path.realpath(file_path)
        try:
            with open(file_path, 'w') as mod_raw:
                mod_raw.write(data)
                return True
        except Exception as err:
            fs_env['errors'].append(str(err))
            return False

    @staticmethod
    def json(file_path, obj):
        file_path = os.path.realpath(file_path)
        with open(file_path, 'w') as mod_raw:
            try:
                data = json.dumps(obj)
                mod_raw.write(data)
                return True
            except Exception as err:
                fs_env['errors'].append(str(err))
                return False


#  /app/instance.py


#  import json  # duplicate :: commented by /build/__packager.py
import requests
import re
from requests.auth import HTTPProxyAuth
from urllib.parse import quote, urlparse
import cloudscraper


class Instance:
    def __init__(self, pref):
        self.pref = pref

        # Globals
        self.null_image = 'https://elx.ai/cdn/public/assets/null-image.png'

        self.errors = list()
        self.__types = dict(object=dict, array=list, int=int, string=str, bool=bool, float=float, number=int)

        def __isX(haystack, needle):
            __typ = self.__types[needle.lower()] if needle.lower() in self.__types else str
            return isinstance(haystack, __typ)

        self.isX = __isX

        self.__card_types = '4:VI|5:MC|3:AE|6:DI'

        def __get_card_type(card_number):
            return {
                k.split(':')[0]: k.split(':')[1] for k in self.__card_types.split('|')
            }[card_number[0]] if card_number[0] in ['3', '4', '5', '6'] else 'null'

        self.get_card_type = __get_card_type

        self.states_us = [
            "AL", "AK", "AS", "AZ", "AR", "AF", "AA", "AC", "AE", "AM", "AP", "CA", "CO", "CT", "DE", "DC",
            "FM", "FL", "GA", "GU", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MH", "MD", "MA",
            "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "MP", "OH", "OK",
            "OR", "PW", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VI", "VA", "WA", "WV", "WI",
            "WY"
        ]
        self.states_us_parsed = {
            "AL": "Alabama",
            "AK": "Alaska",
            "AS": "American Samoa",
            "AZ": "Arizona",
            "AR": "Arkansas",
            "CA": "California",
            "CO": "Colorado",
            "CT": "Connecticut",
            "DE": "Delaware",
            "DC": "District Of Columbia",
            "FM": "Federated States Of Micronesia",
            "FL": "Florida",
            "GA": "Georgia",
            "GU": "Guam",
            "HI": "Hawaii",
            "ID": "Idaho",
            "IL": "Illinois",
            "IN": "Indiana",
            "IA": "Iowa",
            "KS": "Kansas",
            "KY": "Kentucky",
            "LA": "Louisiana",
            "ME": "Maine",
            "MH": "Marshall Islands",
            "MD": "Maryland",
            "MA": "Massachusetts",
            "MI": "Michigan",
            "MN": "Minnesota",
            "MS": "Mississippi",
            "MO": "Missouri",
            "MT": "Montana",
            "NE": "Nebraska",
            "NV": "Nevada",
            "NH": "New Hampshire",
            "NJ": "New Jersey",
            "NM": "New Mexico",
            "NY": "New York",
            "NC": "North Carolina",
            "ND": "North Dakota",
            "MP": "Northern Mariana Islands",
            "OH": "Ohio",
            "OK": "Oklahoma",
            "OR": "Oregon",
            "PW": "Palau",
            "PA": "Pennsylvania",
            "PR": "Puerto Rico",
            "RI": "Rhode Island",
            "SC": "South Carolina",
            "SD": "South Dakota",
            "TN": "Tennessee",
            "TX": "Texas",
            "UT": "Utah",
            "VT": "Vermont",
            "VI": "Virgin Islands",
            "VA": "Virginia",
            "WA": "Washington",
            "WV": "West Virginia",
            "WI": "Wisconsin",
            "WY": "Wyoming"
        }

        # Success class
        class Response:
            def __init__(self, b):
                self.text = json.dumps(dict(success=b))
        self.Response = Response

        def __get_state_id(state):
            return self.states_us.index(state) + 1 if state in self.states_us else None

        self.get_state_id = __get_state_id

        def __json_to_form_data(obj):
            return '&'.join(
                [
                    f'{quote(str(k))}={quote(str(v))}' if '^' not in str(v) else (
                        '&'.join([f'{quote(str(k))}={quote(str(x))}' for x in str(v).split('^')])
                    ) for k, v in obj.items()
                ]
            ) if self.isX(obj, 'object') else ''

        self.j2f = __json_to_form_data

        def __add_error(typ, err):
            __matches = [k for k, v in enumerate(self.errors) if v['type'] == typ]
            return self.errors.append(dict(type=typ, msg=[err])) if \
                len(__matches) <= 0 else self.errors[__matches[0]]['msg'].append(err)

        self.add_error = __add_error

        def __echo_errors():
            print(json.dumps(self.errors, indent=2))

        self.echo_errors = __echo_errors

        __comp_char = '|'

        def __cc(s):
            return s.split(__comp_char)

        def __validate(__self, data, **kwargs):
            __res = []
            for typ in kwargs:
                array = kwargs[typ]
                __imports = [
                    dict(
                        value=__cc(i)[0],
                        type=__cc(i)[1],
                        empty=False
                    ) if len(__cc(i)) == 2 else (
                        dict(
                            value=__cc(i)[0],
                            type=__cc(i)[1],
                            empty=__cc(i)[2] == 'empty'
                        ) if len(__cc(i)) > 2 else (
                            dict(value=i, type='string', empty=False)
                        )
                    ) for i in array
                ]
                __msg = '%s'
                __filter_imports = [
                    __self.add_error(typ, __msg % x['value']) for x in __imports
                    if not x['value'] in data or not (
                            (
                                    x['empty'] and __self.isX(data[x['value']], x['type'])
                            ) or (
                                    not x['empty'] and __self.isX(data[x['value']], x['type'])
                                    and bool(data[x['value']])
                            )
                    )
                ]
                __res.append(len(__filter_imports) <= 0)

            return __res

        self.validate = __validate

        def __is_valid():
            return len(self.errors) <= 0
        self.is_valid = __is_valid

        self.imports = [
            "profile|object|empty",
            "size|string",
            # "qty|string",
        ]
        self.validate(self, self.pref, imports=self.imports)

        self.__required_profile = [
            "profileName|string",
            "firstName|string",
            "lastName|string",
            "phoneNumber|string",
            "email|string",
            "shippingAddress1|string",
            "shippingAddress2|string|empty",
            "zipcode|string",
            "city|string",
            "state|string",
            "stateName|string",
            "country|string",
            "countryIso|string",
            "cardFullName|string",
            "cardType|string",
            "cardNumber|string",
            "cardCVC|string",
            "cardExpirationMonth|string",
            "cardExpirationYear|string",
        ]
        if 'profile' in self.pref and isinstance(self.pref['profile'], dict):
            self.pref['profile']['stateName'] = self.states_us_parsed[
                self.pref['profile']['state']
            ] if 'state' in self.pref['profile'] and self.pref['profile']['state'] in self.states_us_parsed else ''
            if 'countryIso' not in self.pref['profile']:
                self.pref['profile']['countryIso'] = 'US'
            self.validate(self, self.pref['profile'], profile=self.__required_profile)
        else:
            self.add_error(
                'profile', 'pref is missing { profile } object'
            )

        # App::Requests:/Session
        self.session = cloudscraper.create_scraper() if 'cloudflare' in pref and pref['cloudflare'] else \
            requests.Session()
        # App::Proxy
        if 'proxy' in self.pref and self.pref['proxy'] and not self.pref['proxy'] == 'localhost':
            self.proxy_format = ['host', 'port', 'username', 'password']
            self.parsed_proxy = {
                v: self.pref['proxy'].split(':')[k] for k, v in enumerate(self.proxy_format)
                if k < len(self.pref['proxy'].split(':'))
            } if isinstance(self.pref['proxy'], str) else (
                self.pref['proxy'] if isinstance(self.pref['proxy'], dict) else {}
            )

            self.pref['proxy'] = self.parsed_proxy
            self.__proxy = self.parsed_proxy

            # __proxy_format = [
            #     'host|string',
            #     'port|string',
            #     'username|string|empty',
            #     'password|string|empty'
            # ]
            # self.__proxy = self.validate(
            #     self, self.pref['proxy'], proxy=__proxy_format
            # )[0] if 'proxy' in self.pref and isinstance(self.pref['proxy'], dict) else False

            if self.__proxy:
                prox = self.pref['proxy']
                loc = f"{prox['host']}:{str(prox['port'])}"
                auth = f"{prox['username']}:{prox['password']}" if 'username' in prox and 'password' in prox else None
                self.default_proxy = f"{loc}:{auth}" if auth else loc
                self.at_proxy = f"{auth}@{loc}" if auth else loc

                self.parsed_proxy = {**self.pref['proxy'], **{
                    'protocol': self.pref['proxy']['protocol'] if 'protocol' in self.pref['proxy'] else 'http'
                }}
                self.proxy = {
                    'proxies': {
                        'http': f"http://{self.at_proxy}",
                        'https': f"https://{self.at_proxy}"
                    },
                    'auth': HTTPProxyAuth(prox['username'], prox['password']) if auth else None
                }

                self.session.proxies = self.proxy['proxies']
                if auth:
                    self.session.auth = HTTPProxyAuth(prox['username'], prox['password'])
            else:
                self.default_proxy = None
                self.parsed_proxy = None
        else:
            self.default_proxy = None
            self.parsed_proxy = None


#  /app/observer.py


#  import os  # duplicate :: commented by /build/__packager.py
#  import json  # duplicate :: commented by /build/__packager.py


class Observer:
    @staticmethod
    def json(res):
        try:
            res = json.loads(res)
            return res
        except Exception as err:
            __foo = str(err)
            return False

    @staticmethod
    def validate(callee, c):
        _caller = callee()
        _headers = _caller.headers if hasattr(_caller, 'headers') else {}
        res = _caller.text
        f = callee.__name__
        c = {k: {**dict(inverse=False, obj=False, json=False, headers=False), **v} for k, v in c.items()}
        if len([k for k, v in c.items() if 'key' not in v or not isinstance(v, dict)]) > 0:
            return print('Invalid @Observer.validate: all { .. props } must have at least a { "key" }.')
        c[f]['key'] = [c[f]['key']] if not isinstance(c[f]['key'], list) else c[f]['key']
        r = (Observer.json(res) if c[f]['json'] else (_headers if c[f]['headers'] else res)) if f in c else False
        render = r is not False and (
            len([x for x in c[f]['key'] if x in r]) > 0 and len([
                x for x in c[f]['key'] if x in r and isinstance(r[x], dict)
            ]) > 0 if c[f]['obj'] else (len([
                    x for x in c[f]['key'] if x in r
                ]) > 0 and len([
                    x for x in c[f]['key'] if x in r and r[x] == c[f]['matches']
                ]) > 0 if 'matches' in c[f] and isinstance(r, dict)
                else len([
                    x for x in c[f]['key'] if x in r
                ]) > 0
            )
        )

        return (not render, _caller,) if c[f]['inverse'] else (render, _caller,)

#  /app/px.py


#  import requests  # duplicate :: commented by /build/__packager.py
import time
import base64
#  import json  # duplicate :: commented by /build/__packager.py


class PerimeterX:
    @classmethod
    def genKey(cls):
        t = f'94V+Wirg3s+h4q52gF6cWw==:palacebot:{int(round(time.time() * 1000))}:' \
            f'7OHWdszZs57e5UbyzcFMjQydrjlaOB8+f5flMiSrQb880Sxt8r3tgH5ocpC19qh5'

        result = []

        for i in range(0, len(t), 4):
            result.append((base64.b64encode((t[i: i + 4]).encode("utf-8"))).decode("utf-8"))

        key = (base64.b64encode(("".join(result)).encode("utf-8"))).decode("utf-8")
        return key

    @staticmethod
    def get(site, params=None):
        if params is None:
            params = {}
        headers = {
            'x-palacebot-key': '7OHWdszZs57e5UbyzcFMjQydrjlaOB8+f5flMiSrQb880Sxt8r3tgH5ocpC19qh5'
        }

        body = {
            "key": str(PerimeterX.genKey()),
            "site": site,
            **params
        }
        r = requests.post('https://curvesolutions.dev/94V+Wirg3s+h4q52gF6cWw==/px', headers=headers,
                          data=body, params=params)
        try:
            data = json.loads(r.text)['data']
            if data['userAgent']:
                response = {
                    'success': True,
                    'userAgent': data['userAgent'],
                    'cookies': {k: v for k, v in data.items() if not k == 'userAgent'}
                }
                return response, r,
            else:
                return {
                    'success': False,
                    'data': data,
                    'cookies': {}
                }, r,
        except Exception as exp:
            return dict(success=False, error=str(exp)), r,


#  /app/runtime.py


import colored
from colored import stylize, fg
from datetime import datetime


class Runtime:
    production = False
    @staticmethod
    def log(*args, **kwargs):
        color = kwargs['color'] if 'color' in kwargs else None
        logs = [x + '\n' for x in args]
        for log in logs:
            if Runtime.production:
                print(
                    f"{datetime.now().strftime('%H:%M:%S')} | " + stylize(log, fg(color)) if color else log, flush=True
                )
            else:
                print(log, flush=True)


#  /app/workers.py


#  from observer import Observer  # commented by /build/__packager.py
#  from runtime import Runtime  # commented by /build/__packager.py
#  import time  # duplicate :: commented by /build/__packager.py
import pytz
#  from datetime import datetime  # duplicate :: commented by /build/__packager.py


class Worker:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.env = kwargs['env'] if 'env' in kwargs and isinstance(kwargs['env'], dict) else None
        self.main = kwargs['main'] if 'main' in kwargs and isinstance(kwargs['main'], object) else None
        self.workflow = kwargs['workflow'] if 'workflow' in kwargs and isinstance(kwargs['workflow'], list) and len([
            x for x in kwargs['workflow'] if not len(x) >= 2
        ]) <= 0 else None
        self.blueprint = kwargs['blueprint'] if 'blueprint' in kwargs and isinstance(kwargs['blueprint'], dict) and len(
            [
                k for k, v in kwargs['blueprint'].items() if not isinstance(v, dict)
            ]
        ) <= 0 else None
        self.valid = True
        self.completed = False
        self.targeted_call = None

    @staticmethod
    def default(main, res):
        # Runtime.log(str(res[0]), color='medium_purple_3b')
        # print(Exporter.set(f'{file}.txt', res[1].text))
        # print(res[1].text)
        success, response = res
        return success

    def start(self):
        if not self.env or not self.main or not self.workflow:
            return print(f'Invalid or missing data for {self.__class__.__name__}: ', json.dumps([
                k for k, v in self.kwargs.items() if not vars(self)[k]
            ], indent=4))
        Runtime.log('Starting Worker')
        self.valid = True
        for step in self.workflow:
            if not self.valid:
                # Runtime.log(f'Failed while {step[1][0]}', color='red')
                break
            step = step + (self.__class__.default,) if len(step) < 3 else step
            step = step + (None,) if len(step) < 4 else step
            hibernate = int(str(step[3])[:10]) if len(step) > 3 and isinstance(step[3], int) and len(str(step[3])) > 9 \
                and int(str(step[3])[:10]) > time.time() else None
            if hibernate:
                wait = hibernate - time.time()
                tz = self.env['timezone'] if 'timezone' in self.env else 'US/Eastern'
                time_fmt = datetime.fromtimestamp(hibernate, pytz.timezone(tz)).strftime(
                    '%m/%d/%Y, %H:%M:%S%p'
                )
                Runtime.log(f'Going to hibernate mode \n until {time_fmt} {tz}', color='yellow')
                time.sleep(wait)

            task, log, post_call, hibernate = step
            if self.targeted_call:
                if task == self.targeted_call:
                    self.targeted_call = None
                else:
                    continue
            log_text, log_color = log
            Runtime.log(log_text, color=log_color)
            try:
                attempts = 1
                self.completed = False
                while not self.completed:
                    post_call_response = post_call(self.main, Observer.validate(task, self.blueprint))
                    action, next_call, finish = (tuple(post_call_response) + (None, None,))[:3] if (
                        isinstance(post_call_response, tuple) or isinstance(post_call_response, list)
                    ) and len(post_call_response) > 1 else (post_call_response, None, None,)

                    if finish:
                        self.completed = True
                        self.valid = False
                        break

                    if next_call:
                        self.targeted_call = next_call

                    if action:
                        self.completed = True
                    else:
                        if 'retries' in self.env and task.__name__ in self.env['retries'] and (
                                isinstance(self.env['retries'][task.__name__], int)
                        ):
                            if attempts >= self.env['retries'][task.__name__]:
                                self.completed = True
                                self.valid = False
                                break
                            Runtime.log('Retrying..', color='yellow')
                            time.sleep(
                                self.env['retry_interval'] if 'retry_interval' in self.env and isinstance(
                                    self.env['retry_interval'], int
                                ) or isinstance(self.env['retry_interval'], float) else 3
                            )
                        else:
                            self.completed = True
                            self.valid = False
                            Runtime.log(f'Failed while: {log_text}', color='red')
                            break
                    attempts += 1

            except Exception as err:
                Runtime.log(f'Error while: {log_text}', color='red')
                self.env['errors'].append(f'Error in function f{task.__name__}(): {str(err)}')
                # self.valid = False
                raise err
                break


#  /discord/webhook.py


#  import requests  # duplicate :: commented by /build/__packager.py
#  import json  # duplicate :: commented by /build/__packager.py

env = {
    'webhook': {
        # 'private': 'https://discord.com/api/webhooks/750941418788487209/ltQH_xT8UkOveQG0ZtFe8hxWsMmVF40P01-'
        #            'EONlFfngexk3hIQ5w2tZqYdRrW7TnegiC',
        # 'public': 'https://discord.com/api/webhooks/745102515309117602/'
        #           '_VKn2-0MTHqEgRfl_PttQniUaUZI8dgxOaROa6T2yUF1vjcwIHPQM362LfbT5Mf3_N0t',
        # 'admin': 'https://discord.com/api/webhooks/733806441965551696/'
        #          'ybyBsJsj9RvudwgNiQkMpuGPqEDsSad36qluRFfuJfW6gUgcO14d7_mw3-JdzNb0FZ8n'
    },
    'colors': {
        'purple': 10181046,
        'green': 2879580,  # 2bf05c
        'red': 16080725,  # f55
        'blue': 7785669,
        'default': 7785669
    }
}


def change_webhook(webhook):
    env['webhook'] = webhook
    return True


class PalaceBot:
    @staticmethod
    def get_payload(title, color, image, fields):
        return {
            "username": "Palace Bot",
            "avatar_url": "https://cdn.discordapp.com/attachments/579704823360913410/743147285873033226/pb1.jpg",
            "content": "",
            "embeds": [
                {
                    "author": {
                        "name": "Palace Bot",
                        "icon_url": "https://cdn.discordapp.com/attachments/579704823360913410/743147285873033226/"
                                    "pb1.jpg"
                    },
                    "title": title,
                    "color": color,
                    "url": "",
                    "fields": fields,
                    "thumbnail": {
                        "url": image
                    },
                    "footer": {
                        "text": "PalaceBotIO",
                        "icon_url": "https://cdn.discordapp.com/attachments/579704823360913410/743147285873033226/"
                                    "pb1.jpg"
                    }
                }
            ]
        }

    @staticmethod
    def get_headers():
        return {
            'Content-Type': 'application/json',
            'Cookie': '__cfduid=da70fff465cc49b790ffa5a1546db64d91595038468;'
                      ' __cfruid=505e7434e3333ded2bbbcffbac5b10bb52bbe000-1596909913',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
        }

    @staticmethod
    def send(headers, payload, type=None):
        type = type if isinstance(type, list) else (
            [type] if isinstance(type, str) else ['private, admin']
        )
        try:
            for typ in type:
                if typ not in env['webhook']:
                    continue
                response = requests.request(
                    "POST", env['webhook'][typ],
                    headers=headers, data=json.dumps(payload)
                )
        except Exception as exp:
            return False, str(exp),
        return True, 'ok',


class Webhook:
    @staticmethod
    def send(msg, color, product_image, type=None, **kwargs):
        try:
            if type is None:
                type = ['private', 'admin']
            kwargs = [{'name': ' '.join(k.split('_')), 'value': v} for k, v in kwargs.items()]
            payload = PalaceBot.get_payload(
                msg,
                env['colors'][color] if color in env['colors'] else env['colors']['default'],
                product_image,
                kwargs
            )
            headers = PalaceBot.get_headers()
            return PalaceBot.send(headers, payload, type)
        except:
            pass


class PublicWebhook:
    @staticmethod
    def send(product_name, user_size, fr_cookie, fr_cid_cookie, product_image):
        payload = PalaceBot.get_payload(
            'Product Successfully Added To Cart',
            env['colors']['blue'],
            product_image,
            [
                {
                    "name": "Product",
                    "value": product_name
                }, {
                    "name": "Size",
                    "value": user_size,
                    "inline": True
                }, {
                    "name": "Front End Cookie",
                    "value": f'||{fr_cookie}||'
                }, {
                    "name": "Front End CID Cookie",
                    "value": f'||{fr_cid_cookie}||'
                }
            ]
        )
        headers = PalaceBot.get_headers()
        return PalaceBot.send(headers, payload)

    @staticmethod
    def send_checkout(product_name, user_size, product_image, success=False, msg="Payment Declined"):
        payload = PalaceBot.get_payload(
            msg,
            env['colors']['green'] if success else env['colors']['red'],
            product_image,
            [
                {
                    "name": "Product",
                    "value": product_name
                }, {
                    "name": "Size",
                    "value": user_size,
                    "inline": True
                }, {
                    "name": "Status",
                    "value": 'Successful Checkout' if success else 'Checkout Failed'
                }, {
                    "name": "Order ID" if success else "Reason",
                    "value": msg
                }
            ]
        )
        headers = PalaceBot.get_headers()
        return PalaceBot.send(headers, payload)

    @staticmethod
    def send_paypal(product_name, user_size, product_image, success=True, paypal_url=None):
        payload = PalaceBot.get_payload(
            "Paypal checkout URL received" if success else "Error generating Paypal URL",
            env['colors']['blue'] if success else env['red'],
            product_image,
            [
                {
                    "name": "Product",
                    "value": product_name
                }, {
                    "name": "PayPal URL",
                    "value": f'[Click Here]({paypal_url})' if paypal_url else 'N/A'
                }, {
                    "name": "Size",
                    "value": user_size,
                    "inline": True
                }, {
                    "name": "Status",
                    "value": 'Awaiting Payment' if success else 'Error generating Paypal URL'
                }
            ]
        )
        headers = PalaceBot.get_headers()
        return PalaceBot.send(headers, payload)


class HibbettWebhook:
    @staticmethod
    def send(mode, product_name, product_id, product_image, variant, order_number, msg="Order Has Been Placed."):
        payload = PalaceBot.get_payload(
            msg, env['colors']['green'], product_image,
            [
                    {
                        "name": "Product",
                        "value": product_name
                    }, {
                        "name": "Variant",
                        "value": variant,
                        "inline": True
                    }, {
                        "name": "Store",
                        "value": "Hibbett",
                        "inline": True
                    }, {
                        "name": "Mode",
                        "value": mode.title() + ' Mode',
                        "inline": True
                    }, {
                        "name": "Product ID",
                        "value": product_id
                    }, {
                        "name": "Order Number",
                        "value": f'||{order_number}||'
                    }
            ]
        )
        headers = PalaceBot.get_headers()
        return PalaceBot.send(headers, payload)


class EblensWebhook:
    @staticmethod
    def send(product_name, product_id, product_image, variant, order_number, msg="Order Has Been Placed."):
        payload = PalaceBot.get_payload(
            msg, env['colors']['green'], product_image,
            [
                    {
                        "name": "Product",
                        "value": product_name
                    }, {
                        "name": "Variant",
                        "value": variant,
                        "inline": True
                    }, {
                        "name": "Store",
                        "value": "Eblens",
                        "inline": True
                    }, {
                        "name": "Product ID",
                        "value": product_id
                    }, {
                        "name": "Order Number",
                        "value": f'||{order_number}||'
                    }
            ]
        )
        headers = PalaceBot.get_headers()
        return PalaceBot.send(headers, payload)


class GamestopWebhook:

    @staticmethod
    def send(mode, product_name, product_id, product_image, price, order_number, msg="Order Has Been Placed."):
        payload = PalaceBot.get_payload(
            msg, env['colors']['green'], product_image,
            [
                    {
                        "name": "Product",
                        "value": product_name
                    }, {
                        "name": "Price",
                        "value": price,
                        "inline": True
                    }, {
                        "name": "Store",
                        "value": "Gamestop",
                        "inline": True
                    }, {
                        "name": "Mode",
                        "value": mode.title() + ' Mode',
                        "inline": True
                    }, {
                        "name": "Product ID",
                        "value": product_id
                    }, {
                        "name": "Order Number",
                        "value": f'||{order_number}||'
                    }
            ]
        )
        headers = PalaceBot.get_headers()
        return PalaceBot.send(headers, payload)

    @staticmethod
    def declined(mode, product_name, product_id, product_image, price, message, msg="Payment Declined"):
        payload = PalaceBot.get_payload(
            msg, env['colors']['red'], product_image,
            [
                    {
                        "name": "Product",
                        "value": product_name
                    }, {
                        "name": "Price",
                        "value": price,
                        "inline": True
                    }, {
                        "name": "Store",
                        "value": "Gamestop",
                        "inline": True
                    }, {
                        "name": "Mode",
                        "value": mode.title() + ' Mode',
                        "inline": True
                    }, {
                        "name": "Product ID",
                        "value": product_id
                    }, {
                        "name": "Message",
                        "value": f'{message}'
                    }
            ]
        )
        headers = PalaceBot.get_headers()
        return PalaceBot.send(headers, payload)
