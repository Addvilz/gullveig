import logging
from configparser import ConfigParser
from os import path, listdir

LOGGER = logging.getLogger('gullveig')


def priority_sort_files(k: str):
    first = 0
    second = k

    if '-' not in k:
        return first, second

    parts = k.split('-', 2)

    # noinspection PyBroadException
    try:
        first = int(parts[0])
        second = parts[1]
    except BaseException:
        pass

    return first, second


class ConfigurationError(RuntimeError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Configuration(ConfigParser):
    def __init__(self, file_path: str, defaults: dict, required: dict = {}) -> None:
        self.__file_path = path.realpath(file_path)
        self.__dirname = path.dirname(self.__file_path)
        self.__defaults = defaults
        self.__required = required
        super().__init__()

    def is_file_path_valid(self):
        return path.exists(self.__file_path) and path.isfile(self.__file_path)

    def resolve_config_path(self, to_resolve):
        if path.isabs(to_resolve):
            return to_resolve

        return path.abspath(path.join(
            self.__dirname,
            to_resolve
        ))

    def initialize(self):
        files_to_read = [
            self.__file_path
        ]

        # Scan for additional configuration files to read
        d_directory = '%s.d/' % self.__file_path

        if path.isdir(d_directory):
            d_files = sorted(listdir(d_directory), key=priority_sort_files)

            for d_file in d_files:
                if d_file[-5:] != '.conf':
                    continue

                files_to_read.append(path.join(d_directory, d_file))

        LOGGER.debug('Loading configuration files, in order: %s', ', '.join(files_to_read))

        self.read(files_to_read, encoding='utf-8')

        # Load defaults. Slightly different than DEFAULT behavior
        for section, section_values in self.__defaults.items():
            if not self.has_section(section):
                self[section] = section_values
                continue
            for key, value in section_values.items():
                if not self.has_option(section, key):
                    self.set(section, key, value)

        for section, keys in self.__required.items():
            if not self.has_section(section):
                raise ConfigurationError(
                    'Missing mandatory configuration section %s in file %s'
                    % (section, self.__file_path)
                )
            for key in keys:
                if not self.has_option(section, key):
                    raise ConfigurationError(
                        'Missing mandatory configuration key %s in section %s, in file %s'
                        % (key, section, self.__file_path)
                    )
