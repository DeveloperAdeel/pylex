import requests
import json

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


