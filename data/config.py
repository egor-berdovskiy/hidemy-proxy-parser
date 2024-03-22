from configparser import ConfigParser


parser = ConfigParser()
parser.read(r'config.ini')


class Parser:
    section = 'Parser'
    base_url = parser.get(section, 'base_url')
    ports = parser.get(section, 'ports')  # 80,1233,1337
    max_time = parser.get(section, 'max_time')
    type = parser.get(section, 'type')  # h + s (http + https)
    countries = parser.get(section, 'countries')  # KZ + RU + ??
    silent_mode = parser.getboolean(section, 'silent_mode')
    next_page_delay = parser.getfloat(section, 'next_page_delay')


class Output:
    section = 'Output'
    proxy_count = parser.get(section, 'proxy_count')  # int or all
    save_dir = parser.get(section, 'save_dir')
    file_marker = parser.get(section, 'file_marker')  # date or uuid4
