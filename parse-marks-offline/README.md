### Generated: [`res.json`](./res.json)

# Requirements

`python3`, `python3-pip`, can be installed by,

```sh
$ sudo apt install python3 python3-pip
```

# Quickstart

1. See `config.py` for sample URLs.

2. Execute

```sh
$ pip3 install requests beautifulsoup4
$ python3 parse.py -r <RESPONSE_URL> -k <KEY_URL> -o <FILE_NAME>
```

```cmd
$ python3 parse.py -h
usage: parse.py [-h] [-r RESPONSE_URL] [-k ANSWER_KEY_URL] [-o FILE_NAME]

Parses candidate's response sheet, calculates marks, and stores results as JSON.

optional arguments:
  -h, --help            show this help message and exit
  -r RESPONSE_URL, --response RESPONSE_URL
                        Candidate's response key URL.
  -k ANSWER_KEY_URL, --key ANSWER_KEY_URL
                        Answer key URL.
  -o FILE_NAME          Print output to file.
```

Alternatively, `make` and `make t` can be used for convenience.

# Notes

1. It's working so far. there's [`crawler.py`](./crawler.py) as well, which scrapes the website, and extracts data for answer key. (e.g. set2)

2. ~~not tested much (will do).~~ -> Tested on my response sheet, cross checked with pragy's. Results match.

3. It is assumed that the answer key always has `short_id` in sorted order, i.e. g1-g10 first, then c1-c55.

4. if `-o` is not provided, the program prints output to `stdout`.
