from bs4 import BeautifulSoup
import requests as r

# there's some issue of ids around Q.48 of CS, so need to change these pointers midway between.
start = 357482
end = 357489

# hacky way of generating answer key by scraping gateoverflow.in manually.
# no use currently.
for i in range(end, start-1, -1):
    link = f'https://gateoverflow.in/{i}'
    res = BeautifulSoup(r.get(link).text, 'html.parser')
    title = res.find_all('span', itemprop='name')[0].text
    res = res.find_all('button', {'class': ['btn', 'btn-info']})[0]
    # and some editor magic
    print(f'{title},{res.text}')
