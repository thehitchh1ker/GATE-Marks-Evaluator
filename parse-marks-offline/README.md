# Requirements

`python3`, `python3-pip`, can be installed by,

```sh
$ sudo apt install python3 python3-pip
```

# Quickstart

1. Edit `config.py` and enter the required URLs.

2. Execute

```sh
$ pip3 install requests beautifulsoup4
$ python3 parse.py
```

Alternatively, `make` and `make t` can be used for convenience.

# Notes

1. doesn't work right now because actual response sheet is already jumbled, so order needs to be decided with long_id, which isn't available in the google sheet.

2. not tested much (will do, when 1. is fixed).
