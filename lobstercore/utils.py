from time import mktime

import configparser
import datetime
import json
import os


class DatetimeJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))
        return json.JSONEncoder.default(self, obj)


def get_config(base_dir):
    config = configparser.ConfigParser()
    config.optionxform = str

    config.read("{}/lobstercms.defaults.conf".format(base_dir))

    if os.path.isfile("{}/lobstercms.conf".format(base_dir)):
        config.read("{}/lobstercms.conf".format(base_dir))

    return config
