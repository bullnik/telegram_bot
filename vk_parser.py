import requests
from bs4 import BeautifulSoup

vk_domain = 'https://vk.com/'


def get_html(url, params=None):
    r = requests.get(url, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    h2name = soup.find('h2', class_='op_header')
    if h2name:
        name = h2name.get_text()
        return name
    return "Пользователей с таким id не найдено"


def parse(vk_id):
    html = get_html(vk_domain + vk_id)
    if html.status_code == 200 and html:
        return get_content(html.text)
    else:
        return "Пользователей с таким id не найдено"
