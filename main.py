from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import os
import links

def criar_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options)
    return driver

def get_html(driver, url):
    driver.get(url)
    WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'Opta-Stat')))
    html = driver.page_source
    return html

def get_equipes(soup):
    ul_times = soup.find('ul', class_='Opta-Cf')
    times_html = ul_times.find_all('a')[1:]
    casa, fora = [team.text for team in times_html][:2]
    return casa, fora

def get_colunas(soup):
    colunas_html = soup.find_all('th', class_='Opta-Stat')[:15]
    colunas = [col_html.text for col_html in colunas_html]
    colunas.insert(0, 'Jogador')
    return colunas

def get_jogadores(soup):
    jogadores_html = soup.find_all('th', class_='Opta-Player')
    jogadores = [jog_html.text for jog_html in jogadores_html]
    jogadores.pop(0)
    
    indice = jogadores.index('')
    for _ in range(indice+1):
        jogadores.pop(0)
    
    while 'Total' in jogadores:
        jogadores.remove('Total')

    jogadores_casa = []
    i = 0
    jogador = jogadores[i]
    while jogador != '':
        jogadores_casa.append(jogador)
        i += 1
        jogador = jogadores[i]

    jogadores_fora = jogadores[i+1:]
    return jogadores_casa, jogadores_fora

def get_stats(soup):
    
    jogadores_casa, jogadores_fora = get_jogadores(soup)

    estatisticas_html = soup.find_all('td', class_='Opta-Stat')
    estatisticas = [stat.text for stat in estatisticas_html]

    end_casa = len(jogadores_casa) * 15
    start_fora = end_casa
    end_fora = start_fora + (15 * len(jogadores_fora))

    stats_casa = estatisticas[:end_casa]
    stats_fora = estatisticas[start_fora:end_fora]

    linhas_casa = []
    linhas_fora = []

    for i in range(len(stats_casa)//15):
        linhas_casa.append([jogadores_casa[i]])
        for num in stats_casa[i*15:i*15+15]:
            linhas_casa[-1].append(num)

    for i in range(len(stats_fora)//15):
        linhas_fora.append([jogadores_fora[i]])
        for num in stats_fora[i*15:i*15+15]:
            linhas_fora[-1].append(num)
    

    return linhas_casa, linhas_fora

def criar_pasta(nome_pasta):
    path = os.getcwd() + '\\Equipes\\' + nome_pasta
    os.makedirs(path, exist_ok=True)


def main(urls: list, driver=None):

    if not driver:
        driver = criar_driver()
        

    for i,url in enumerate(urls):

        print(f'url: {i}/{len(urls)}')

        # Pegar HTML da URL
        html = get_html(driver, url)
        soup = BeautifulSoup(html, 'html.parser')

        # Pegar as informações do html
        casa, fora = get_equipes(soup)
        colunas = get_colunas(soup)
        linhas_casa, linhas_fora = get_stats(soup)

        # Criar tabelas de cada time
        tab_casa = {coluna: [] for coluna in colunas}
        tab_fora = {coluna: [] for coluna in colunas}

        

        path_casa = os.path.join(os.getcwd(), 'Equipes', casa, f'{casa}.csv')
        path_fora = os.path.join(os.getcwd(), 'Equipes', fora, f'{fora}.csv')

        # Criar pastas de cada time
        if not os.path.exists(path_casa):
            criar_pasta(casa)
            df_casa = pd.DataFrame(tab_casa)
            for linha in linhas_casa:
                df_casa.loc[len(df_casa)] = linha

        else:
            df_casa = pd.read_csv(path_casa)
            for linha in linhas_casa:
                df_casa.loc[len(df_casa)] = linha

        if not os.path.exists(path_fora):
            criar_pasta(fora)
            df_fora = pd.DataFrame(tab_fora)
            for linha in linhas_fora:
                df_fora.loc[len(df_fora)] = linha
        else:
            df_fora = pd.read_csv(path_fora)
            for linha in linhas_fora:
                df_fora.loc[len(df_fora)] = linha

        # Criando CSV
        df_casa.to_csv(f'.\\Equipes\\{casa}\\{casa}.csv', index=False)
        df_fora.to_csv(f'.\\Equipes\\{fora}\\{fora}.csv', index=False)


            


# url = 'https://optaplayerstats.statsperform.com/pt_BR/soccer/brasileir%C3%A3o-s%C3%A9rie-a-2024/a2yu8vfo8wha3vza31s2o8zkk/match/view/9s0xz8zqc4s5yzg9hqqmj2978/match-summary'
# main([url])

url = 'https://optaplayerstats.statsperform.com/pt_BR/soccer/brasileir%C3%A3o-s%C3%A9rie-a-2024/a2yu8vfo8wha3vza31s2o8zkk/opta-player-stats'

urls, driver = links.main(url)

main(urls, driver)
