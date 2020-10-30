import json
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
            "url|string",
            "profile|object|empty",
            "size|string",
            "qty|string",
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
