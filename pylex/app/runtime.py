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
