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
$ python3 parse.py -r <RESPONSE_URL> -k <KEY_URL>
```

Alternatively, `make` and `make t` can be used for convenience.

# Notes

1. It's working so far. there's [`crawler.py`](./crawler.py) as well, which scrapes the website, and extracts data for answer key. (e.g. set2)

2. not tested much (will do).
