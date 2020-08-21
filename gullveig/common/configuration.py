import os
from configparser import ConfigParser


class ConfigurationError(RuntimeError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Configuration(ConfigParser):
    def __init__(self, file_path: str, defaults: dict, required: dict = {}) -> None:
        self.__file_path = os.path.realpath(file_path)
        self.__dirname = os.path.dirname(self.__file_path)
        self.__defaults = defaults
        self.__required = required
        super().__init__()

    def is_file_path_valid(self):
        return os.path.exists(self.__file_path) and os.path.isfile(self.__file_path)

    def resolve_config_path(self, path):
        if os.path.isabs(path):
            return path

        return os.path.abspath(os.path.join(
            self.__dirname,
            path
        ))

    def initialize(self):
        self.read(self.__file_path, encoding='utf-8')

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
