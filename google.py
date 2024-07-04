print('from bs4 import BeautifulSoup'.ljust(59), end='\r')
from bs4 import BeautifulSoup
print('from selenium import webdriver'.ljust(59), end='\r')
from selenium import webdriver
print('from selenium.webdriver.common.by import By'.ljust(59), end='\r')
from selenium.webdriver.common.by import By
print('from selenium.webdriver.support.ui import WebDriverWait'.ljust(59), end='\r')
from selenium.webdriver.support.ui import WebDriverWait
print('from selenium.webdriver.support import expected_conditions'.ljust(59), end='\r')
from selenium.webdriver.support import expected_conditions
print('import pandas as pd'.ljust(59), end='\r')
import pandas as pd
print('import os'.ljust(59), end='\r')
import os
print('import time'.ljust(59), end='\r')
import time

def get_html(driver, url):
    driver.get(url)
    time.sleep(2)

    print('Esperando carregamento da página')
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'MzWkAb')))
    
    html = driver.page_source
    return html
    
def get_stats(soup):
    print('Pegando estatísticas')

    all_tr_html = soup.find_all('tr', class_='MzWkAb')
    listas_tr_td_html = [ele.find_all('td') for ele in all_tr_html]

    stats = []
    for td1,td2 in listas_tr_td_html:
        if '%' in td1.text:
            stats.append(int(td1.text[:-1]))
            stats.append(int(td2.text[:-1]))

        else:
            try:
                num = int(td1.text)
            except:
                stats.append(td1.text)
                stats.append(td2.text)
            else:
                stats.append(int(td1.text))
                stats.append(int(td2.text))

    stats_casa = stats[::2]
    stats_fora = stats[1::2]
    return stats_casa, stats_fora

def get_teams_names(soup):
    all_times = soup.find_all('div', class_='liveresults-sports-immersive__hide-element')[:2]
    casa = all_times[0].text
    fora = all_times[1].text
    return casa, fora

def verificar_erro(stats):
    for stat in stats:
        if isinstance(stat, str):
            return True
    return False

def create_df(stats_casa, stats_fora):
    print('Criando DataFrames')
    colunas = ['Adversário', 'Chutes', 'Chutes a gol', 'Posse', 'Passes', 'Precisão Passe', 'Faltas', 'Cartões Amarelos', 'Cartões Vermelhos', 'Impedimentos', 'Escanteios']
    tab_casa = {coluna: [stats_casa[i]] for i,coluna in enumerate(colunas)}
    tab_fora = {coluna: [stats_fora[i]] for i,coluna in enumerate(colunas)}
    df_casa = pd.DataFrame(tab_casa)
    df_fora = pd.DataFrame(tab_fora)
    return df_casa, df_fora

def create_csv(df, path):
    print('Criando/atualizando tabela csv')
    df.to_csv(path, index=False)

def update_csv(new_data, path_base):
    print('Atualizando tabela csv')
    base = pd.read_csv(path_base)
    base.loc[len(base)] = new_data
    base = base.drop_duplicates()
    create_csv(base, path_base)

def main(urls):

    # Configurações do webdriver
    print('Configurando o driver')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--ignore-certificate-errors')

    with webdriver.Chrome(options=options) as driver:
        print('Inicializando driver')
        for url in urls:

            # Pegar o HTML da página
            html = get_html(driver, url)
            soup = BeautifulSoup(html, 'html.parser')

            # Pegar os dados do HTML
            casa, fora = get_teams_names(soup)

            print(f'Partida: {casa} x {fora}')
            stats_casa, stats_fora = get_stats(soup)


            repeticoes = 0
            while verificar_erro(stats_casa) or verificar_erro(stats_fora):
                print('Erro em:')
                print(stats_casa)
                print(stats_fora)
                if repeticoes == 5:
                    print('Não foi possível pegar o html correto')
                    return
                html = get_html(driver, url)
                soup = BeautifulSoup(html, 'html.parser')
                stats_casa, stats_fora = get_stats(soup)
                repeticoes += 1

            stats_casa.insert(0, fora)
            stats_fora.insert(0, casa)

            df_casa, df_fora = create_df(stats_casa, stats_fora)

            # Caminho para as tabelas csv
            path = os.getcwd() + '\\' + 'dados'
            path_casa = f'{path}\\{casa}.csv'
            path_fora = f'{path}\\{fora}.csv'

            # Criar ou atualizar as tabelas csv
            if not os.path.exists(path_casa):
                create_csv(df_casa, path_casa)
            else:
                update_csv(stats_casa, path_casa)

            if not os.path.exists(path_fora):
                create_csv(df_fora, path_fora)
            else:
                update_csv(stats_fora, path_fora)
            
            print(f'\n{casa} x {fora}: bem-sucedido\n')
    
    print('Web Scrapping bem-sucedido')


# urls = ['https://www.google.com/search?sca_esv=9625335c57f85a94&sca_upv=1&cs=1&sxsrf=ADLYWIJqB6HW3VtA7tRsKAgMN2GAetNu7Q:1720032844924&q=Clube+Atl%C3%A9tico+Mineiro&stick=H4sIAAAAAAAAAONgVuLUz9U3MLTMNat6xGjCLfDyxz1hKe1Ja05eY1Tl4grOyC93zSvJLKkUEudig7J4pbi5ELp4FrGKO-eUJqUqOJbkHF5Zkpmcr-CbmZeaWZQPAMYyg-ReAAAA&ved=2ahUKEwjUktnVxYuHAxX9r5UCHVVXCMcQukt6BAgBEBU#sie=m;/g/11y36hpr2s;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nxHVIQmruDWnwTL6DMm0w-fRIRhUxoHPNsJnEnV8zCuM5KLSWnMImIlpppFk_AeipYNPv1FwwzpZBUBlVSSfdvbonUvznept0lvJfSshjU2m85FZvNhYYWz3dx8wDv5Gwv566dzjLlYPXYup3sib3lzPyAN3KJNLH9JlrTIiOd_ROIXaPCU__NNbUn1ni2nBzp4z5hmBml0nN9vtfdxbnmGQpdIJTU52Lrs2-NnEnZk5J3f41w%3D',
#         'https://www.google.com/search?sca_esv=9625335c57f85a94&sca_upv=1&cs=1&sxsrf=ADLYWIJqB6HW3VtA7tRsKAgMN2GAetNu7Q:1720032844924&q=Clube+Atl%C3%A9tico+Mineiro&stick=H4sIAAAAAAAAAONgVuLUz9U3MLTMNat6xGjCLfDyxz1hKe1Ja05eY1Tl4grOyC93zSvJLKkUEudig7J4pbi5ELp4FrGKO-eUJqUqOJbkHF5Zkpmcr-CbmZeaWZQPAMYyg-ReAAAA&ved=2ahUKEwjUktnVxYuHAxX9r5UCHVVXCMcQukt6BAgBEBU#sie=m;/g/11vr1lqhv1;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nxHVIQmruDWnwTL6DMm0w-fRIRhUxoHPNsJnEnV8zCuM5KLSWnMImIlpppFk_AeipYNPv1FwwzpZBUBlVSSfdvbonUvznept0lvJfSshjU2m85FZvNhYYWz3dx8wDv5Gwv566dzjLlYPXYup3sib3lzPyAN3KJNLH9JlrTIiOd_ROIXaPCU__NNbUn1ni2nBzp4z5hmBml0nN9vtfdxbnmGQpdIJTU52Lrs2-NnEnZk5J3f41w%3D',
#         'https://www.google.com/search?sca_esv=9625335c57f85a94&sca_upv=1&cs=1&sxsrf=ADLYWIJqB6HW3VtA7tRsKAgMN2GAetNu7Q:1720032844924&q=Clube+Atl%C3%A9tico+Mineiro&stick=H4sIAAAAAAAAAONgVuLUz9U3MLTMNat6xGjCLfDyxz1hKe1Ja05eY1Tl4grOyC93zSvJLKkUEudig7J4pbi5ELp4FrGKO-eUJqUqOJbkHF5Zkpmcr-CbmZeaWZQPAMYyg-ReAAAA&ved=2ahUKEwjUktnVxYuHAxX9r5UCHVVXCMcQukt6BAgBEBU#sie=m;/g/11vt7q9zcz;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nxHVIQmruDWnwTL6DMm0w-fRIRhUxoHPNsJnEnV8zCuM5KLSWnMImIlpppFk_AeipYNPv1FwwzpZBUBlVSSfdvbonUvznept0lvJfSshjU2m85FZvNhYYWz3dx8wDv5Gwv566dzjLlYPXYup3sib3lzPyAN3KJNLH9JlrTIiOd_ROIXaPCU__NNbUn1ni2nBzp4z5hmBml0nN9vtfdxbnmGQpdIJTU52Lrs2-NnEnZk5J3f41w%3D',
#         'https://www.google.com/search?sca_esv=9625335c57f85a94&sca_upv=1&cs=1&sxsrf=ADLYWIJqB6HW3VtA7tRsKAgMN2GAetNu7Q:1720032844924&q=Clube+Atl%C3%A9tico+Mineiro&stick=H4sIAAAAAAAAAONgVuLUz9U3MLTMNat6xGjCLfDyxz1hKe1Ja05eY1Tl4grOyC93zSvJLKkUEudig7J4pbi5ELp4FrGKO-eUJqUqOJbkHF5Zkpmcr-CbmZeaWZQPAMYyg-ReAAAA&ved=2ahUKEwjUktnVxYuHAxX9r5UCHVVXCMcQukt6BAgBEBU#sie=m;/g/11vt7qsnwd;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nxHVIQmruDWnwTL6DMm0w-fRIRhUxoHPNsJnEnV8zCuM5KLSWnMImIlpppFk_AeipYNPv1FwwzpZBUBlVSSfdvbonUvznept0lvJfSshjU2m85FZvNhYYWz3dx8wDv5Gwv566dzjLlYPXYup3sib3lzPyAN3KJNLH9JlrTIiOd_ROIXaPCU__NNbUn1ni2nBzp4z5hmBml0nN9vtfdxbnmGQpdIJTU52Lrs2-NnEnZk5J3f41w%3D',
#         'https://www.google.com/search?sca_esv=9625335c57f85a94&sca_upv=1&cs=1&sxsrf=ADLYWIJqB6HW3VtA7tRsKAgMN2GAetNu7Q:1720032844924&q=Clube+Atl%C3%A9tico+Mineiro&stick=H4sIAAAAAAAAAONgVuLUz9U3MLTMNat6xGjCLfDyxz1hKe1Ja05eY1Tl4grOyC93zSvJLKkUEudig7J4pbi5ELp4FrGKO-eUJqUqOJbkHF5Zkpmcr-CbmZeaWZQPAMYyg-ReAAAA&ved=2ahUKEwjUktnVxYuHAxX9r5UCHVVXCMcQukt6BAgBEBU#sie=m;/g/11ldrl49tm;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nxHVIQmruDWnwTL6DMm0w-fRIRhUxoHPNsJnEnV8zCuM5KLSWnMImIlpppFk_AeipYNPv1FwwzpZBUBlVSSfdvbonUvznept0lvJfSshjU2m85FZvNhYYWz3dx8wDv5Gwv566dzjLlYPXYup3sib3lzPyAN3KJNLH9JlrTIiOd_ROIXaPCU__NNbUn1ni2nBzp4z5hmBml0nN9vtfdxbnmGQpdIJTU52Lrs2-NnEnZk5J3f41w%3D',
#         'https://www.google.com/search?sca_esv=9625335c57f85a94&sca_upv=1&cs=1&sxsrf=ADLYWIJqB6HW3VtA7tRsKAgMN2GAetNu7Q:1720032844924&q=Clube+Atl%C3%A9tico+Mineiro&stick=H4sIAAAAAAAAAONgVuLUz9U3MLTMNat6xGjCLfDyxz1hKe1Ja05eY1Tl4grOyC93zSvJLKkUEudig7J4pbi5ELp4FrGKO-eUJqUqOJbkHF5Zkpmcr-CbmZeaWZQPAMYyg-ReAAAA&ved=2ahUKEwjUktnVxYuHAxX9r5UCHVVXCMcQukt6BAgBEBU#sie=m;/g/11vt7q340b;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nxHVIQmruDWnwTL6DMm0w-fRIRhUxoHPNsJnEnV8zCuM5KLSWnMImIlpppFk_AeipYNPv1FwwzpZBUBlVSSfdvbonUvznept0lvJfSshjU2m85FZvNhYYWz3dx8wDv5Gwv566dzjLlYPXYup3sib3lzPyAN3KJNLH9JlrTIiOd_ROIXaPCU__NNbUn1ni2nBzp4z5hmBml0nN9vtfdxbnmGQpdIJTU52Lrs2-NnEnZk5J3f41w%3D',
#         'https://www.google.com/search?sca_esv=9625335c57f85a94&sca_upv=1&cs=1&sxsrf=ADLYWIJqB6HW3VtA7tRsKAgMN2GAetNu7Q:1720032844924&q=Clube+Atl%C3%A9tico+Mineiro&stick=H4sIAAAAAAAAAONgVuLUz9U3MLTMNat6xGjCLfDyxz1hKe1Ja05eY1Tl4grOyC93zSvJLKkUEudig7J4pbi5ELp4FrGKO-eUJqUqOJbkHF5Zkpmcr-CbmZeaWZQPAMYyg-ReAAAA&ved=2ahUKEwjUktnVxYuHAxX9r5UCHVVXCMcQukt6BAgBEBU#sie=m;/g/11y36gyxb7;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nxHVIQmruDWnwTL6DMm0w-fRIRhUxoHPNsJnEnV8zCuM5KLSWnMImIlpppFk_AeipYNPv1FwwzpZBUBlVSSfdvbonUvznept0lvJfSshjU2m85FZvNhYYWz3dx8wDv5Gwv566dzjLlYPXYup3sib3lzPyAN3KJNLH9JlrTIiOd_ROIXaPCU__NNbUn1ni2nBzp4z5hmBml0nN9vtfdxbnmGQpdIJTU52Lrs2-NnEnZk5J3f41w%3D',
#         'https://www.google.com/search?sca_esv=9625335c57f85a94&sca_upv=1&cs=1&sxsrf=ADLYWIJqB6HW3VtA7tRsKAgMN2GAetNu7Q:1720032844924&q=Clube+Atl%C3%A9tico+Mineiro&stick=H4sIAAAAAAAAAONgVuLUz9U3MLTMNat6xGjCLfDyxz1hKe1Ja05eY1Tl4grOyC93zSvJLKkUEudig7J4pbi5ELp4FrGKO-eUJqUqOJbkHF5Zkpmcr-CbmZeaWZQPAMYyg-ReAAAA&ved=2ahUKEwjUktnVxYuHAxX9r5UCHVVXCMcQukt6BAgBEBU#sie=m;/g/11y36h6w00;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nxHVIQmruDWnwTL6DMm0w-fRIRhUxoHPNsJnEnV8zCuM5KLSWnMImIlpppFk_AeipYNPv1FwwzpZBUBlVSSfdvbonUvznept0lvJfSshjU2m85FZvNhYYWz3dx8wDv5Gwv566dzjLlYPXYup3sib3lzPyAN3KJNLH9JlrTIiOd_ROIXaPCU__NNbUn1ni2nBzp4z5hmBml0nN9vtfdxbnmGQpdIJTU52Lrs2-NnEnZk5J3f41w%3D']

# Junho até rodada 7 (incluindo rodada 7)
# urls = ['https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7q932m;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
#         'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36h_0zs;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
#         'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qjfx8;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
#         'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36hgc9x;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
#         'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qhv97;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
#         'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1q2fjm;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
#         'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36gyxb7;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
#         'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36hf9z9;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
#         'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qhv98;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
#         'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qzs87;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
#         'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11ldrl5d9m;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
#         'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1mhlgm;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
#         'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7q7bbs;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5']

urls = ['https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7q7qln;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36gst93;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36j4l6x;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7q340b;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7q2n5w;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1mp12w;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36hdc_2;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36hdy07;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qn8ld;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36h2y19;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qb_wv;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36h9p_p;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1m84z0;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1mgwl5;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7q4mm2;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1ndls1;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7q340c;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qzs89;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36j5k98;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11ldrl49tm;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11ldrl570q;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7p1nhh;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qkgkn;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36hm6cm;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36hmq7t;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qb_ww;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qsnwc;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qsnwd;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1mq2zv;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1n14c3;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1n3knw;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qgzqq;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7pm5pj;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1mm0wg;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qdr55;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qf7_0;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36j2n2s;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1lxx43;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7q9zcz;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36hp7xp;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1m361b;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36gvk5w;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1m14kk;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7p6rw6;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qzs8g;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11ldrl5__f;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1lqhv1;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36h3tmp;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qgzqp;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1m1qk6;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vr1mc4ym;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36h9p_q;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36hpr2s;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qf7_2;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36hb0x_;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36htfxm;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7prhm0;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qdr5c;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11y36hzcs6;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5',
        'https://www.google.com/search?q=brasileirao&oq=brasileirao&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg80gEIMjEyMGowajeoAgCwAgA&sourceid=chrome&ie=UTF-8#sie=m;/g/11vt7qjfxc;2;/m/0fnk7q;dt;fp;1;;;&wptab=si:ACC90nw9vMMdwL91whQ4n-NcljM143f3JvZl4TM_hvFSavH6DxhM68nwhpUpFrgEtIyxVqexrdwH9mpql3VkflsXToKZpZUzglpyDUY1ZqELXCrb4sgnv0jgx2XppzXurI-OWdpJSYjBVXC4CDbzJPC1eIDl-iI2aFYCtIGzmnuWtcESvPxFVfy_Jhr1wB0nNNuAY1Bcnos5']

main(urls)