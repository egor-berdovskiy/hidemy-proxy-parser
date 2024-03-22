# HideMy proxy parser
Install dependencies.
```
pip install -r requirements.txt
```
then customize to your requirements config.ini
run main.py
```
py main.py
```
# Config file
[Parser]
1. base_url — do not touch
2. ports — specify ports separated by commas, for example: 80,1234,1337
3. max_time — proxy speed.
4. type — h = http, s = https, 4 = socks4, 5 = socks5, for exemple: sh (http + https)
5. countries — two chars RU + KZ + ??, for example: RUKZ.
6. silent_mode — if true, all pages will be processed by default.
7. next_page_delay — wait time, then go to another page, note that the page may take a long time to load.

[Output]
1. proxy_count — all or any int
2. save_dir — save output files, default ./output/
3. file_marker — is responsible for naming files (date=output-2024-22-03.txt, uuid=output-6ec64ad53583.txt)
