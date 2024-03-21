from selenium_parser import Parser

from data.config import Parser as ParserOptions
from data.config import Output as OutputOptions


def main():
    parser = Parser(
        url=ParserOptions.base_url,
        ports=ParserOptions.ports,
        max_time=ParserOptions.max_time,
        type=ParserOptions.type,
        countries=ParserOptions.countries,
        proxy_count=OutputOptions.proxy_count,
        save_dir=OutputOptions.save_dir,
        file_marker=OutputOptions.file_marker,
    )
    parser.run()


if __name__ == '__main__':
    main()
