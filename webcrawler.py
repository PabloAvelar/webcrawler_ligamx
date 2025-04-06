import cloudscraper
from bs4 import BeautifulSoup
import time

def getPlayers(url, team):
    print(url)

    scraper = cloudscraper.create_scraper()
    html = scraper.get(url).text
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find_all('table')[0]
    thead = table.find_all('thead')[0]
    thead_tr_facts = thead.find_all('tr')[0]
    thead_tr_th_facts = thead_tr_facts.find_all('th')

    thead_tr_data = thead.find_all('tr')[1]
    thead_tr_th_data = thead_tr_data.find_all('th')

    tbody = table.find_all('tbody')[0]
    tbody_tr = tbody.find_all('tr')

    print("JUGADORES!!!!!!")

    jugador = []
    tiempo_jugado = []
    rendimiento = []
    por_90_minutos = []
    pertenece_a = []
    
    for player_row in tbody_tr:
        player_str = ''
        is_null_value = False

        for player_name in player_row.find_all('th'):
            player_str += player_name.text + ","
            player_str = player_str.lower()
            
            player_str = player_str.replace(".", "")
            player_str = player_str.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
            player_str = player_str.replace("ñ", "n")
            player_str = player_str.replace("ü", "u")
            

        for player_data in player_row.find_all('td')[:-1]:
            data = player_data.text.split(" ")

            # Limpiando el dato actual
            data = data[1] if len(data) > 1 else data[0]  # Eliminando la nacionalidad repetida
            data = data.split("-")[0]  # Eliminando el guión de la edad del jugador
            
            
            # Checando si hay datos nulos.
            # Si hay datos nulos, esa fila se elimina y el jugador también.
            if data == '':
                is_null_value = True 
                break
            player_str += data + ","

            if is_null_value:
                break

        # Lista de los datos de la fila del jugador
        player_list = player_str.split(",")
        player_list[0] = player_list[0].replace(" ", "_").lower()

        #generar hechos de prolog
        print(f"EQUIPO: {team}")

        try:
            jugador.append(f"jugador({player_list[0]}, {player_list[1]}, {player_list[2]}, {player_list[3]}).")

            tiempo_jugado.append(f"tiempo_jugado({player_list[0]}, {player_list[4]}, {player_list[5]}, {player_list[6]}, {player_list[7]}).")
            
            rendimiento.append(f"rendimiento({player_list[0]}, {player_list[8]}, {player_list[9]}, {player_list[10]}, {player_list[11]}, {player_list[12]}, {player_list[13]}, {player_list[14]}, {player_list[15]}).")

            por_90_minutos.append(f"por_90_minutos({player_list[0]}, {player_list[16]}, {player_list[17]}, {player_list[18]}, {player_list[19]}, {player_list[20]}).")

            pertenece_a.append(f"pertenece_a({player_list[0]}, {team.lower().replace(' ', '_')}).")
        except IndexError:
            pass

    return [jugador, tiempo_jugado, rendimiento, por_90_minutos, pertenece_a]

def save_facts(*args):
    file = open('ligamx.pl', 'a', encoding='utf-8')
    for fact_list in args:
        for fact_name in fact_list:
            for data in fact_name:
                file.write(data)
                file.write('\n')

    file.write('\n')
    file.close()

def extract_teams(teams):   
    # Extrae los datos de cada equipo
    for team in teams:
        time.sleep(5)
        facts = getPlayers(*team.values(), *team.keys())
        save_facts(facts)

if __name__ == '__main__':
    url = 'https://fbref.com/es/comps/31/Estadisticas-de-Liga-MX'
    scraper = cloudscraper.create_scraper()
    html = scraper.get(url).text
    soup = BeautifulSoup(html, 'html.parser')

    # Extraer la primera tabla donde están los equipos
    teams = []
    table = soup.find_all('table')[1]
    links = table.find_all('a')

    for link in links:
        href = link.get('href')
        teams.append({link.text: 'https://fbref.com' + href})

    extract_teams(teams)