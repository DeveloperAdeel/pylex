from observer import Observer
from runtime import Runtime
import time
import pytz
from datetime import datetime


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
