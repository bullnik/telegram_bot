def __init__():
    try:
        __read_settings()
    except OSError:
        __write_settings(__Settings(10000, 2))


__init__()


class __Settings:
    def __init__(self, max_stored_roads: int,
                 max_count_parsed_roads: int):
        self.max_stored_roads = max_stored_roads
        self.max_count_parsed_roads = max_count_parsed_roads


def __write_settings(settings: __Settings):
    with open('settings.txt', 'w') as settings_file:
        settings_file.write('max_count_parsed_roads: ' + str(settings.max_count_parsed_roads) + '\n'
                            + 'max_stored_roads: ' + str(settings.max_stored_roads))


def __read_settings() -> __Settings:
    with open('settings.txt', 'r') as settings_file:
        settings = __Settings(10000, 1)
        lines = settings_file.readlines()
        for line in lines:
            row = line.split()
            if row[0] == 'max_stored_roads:':
                settings.max_stored_roads = int(row[1])
            elif row[0] == 'max_count_parsed_roads:':
                settings.max_count_parsed_roads = int(row[1])
        return settings


def get_max_stored_roads() -> int:
    settings = __read_settings()
    return settings.max_stored_roads


def set_max_stored_roads(value: int):
    settings = __read_settings()
    settings.max_stored_roads = value
    __write_settings(settings)


def get_max_count_parsed_roads() -> int:
    settings = __read_settings()
    return settings.max_count_parsed_roads


def set_max_count_parsed_roads(value: int):
    settings = __read_settings()
    settings.max_count_parsed_roads = value
    __write_settings(settings)
