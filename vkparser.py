import requests
from bs4 import BeautifulSoup


DOMEN = 'https://vk.com/'


def get_html(url, params=None):
    r = requests.get(url, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    name = soup.find('h2', class_='op_header').get_text()
    return name


def parse(vk_id):
    html = get_html(DOMEN + vk_id)
    if html.status_code == 200:
        return get_content(html.text)
    else:
        return "Ошибка"
