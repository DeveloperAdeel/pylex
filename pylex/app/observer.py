import os
import json


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