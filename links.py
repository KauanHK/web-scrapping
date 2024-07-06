from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

def get_html(driver, url, wait_class: str):
    print('Pegando html: em andamento', end='\r')

    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'Opta-MatchLink')))
    except Exception as e:
        print(f'Pegando HTML: erro: {e}')
    else:
        html = driver.page_source

    print('Pegando html: bem-sucedido', end='\r')
    return html

def get_urls(soup):
    print('Encontrando links: em andamento')

    try:
        links = soup.find_all('a', class_='Opta-MatchLink')
    except Exception as e:
        print(f'Encontrando links: erro: {e}')
    else:
        urls = [link['href'] for link in links]
    
    return urls

def main(url, driver=None):
    print('Configurando o driver')

    if not driver:
        # options.add_argument('--headless')
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Chrome(options)
        

    html = get_html(driver, url, 'Opta-MatchLink')
    soup = BeautifulSoup(html, 'html.parser')
    urls = get_urls(soup)

    return urls, driver
    