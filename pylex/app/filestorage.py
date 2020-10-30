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
