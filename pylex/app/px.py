import requests
import time
import base64
import json


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
