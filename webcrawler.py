import cloudscraper
from bs4 import BeautifulSoup
import time
import unicodedata


def clean_string(string):
    # Limpiar la cadena de caracteres

    string = string.replace(" ", "_")
    string = string.replace(",", "")  # Eliminar comas para cantidades numericas
    string = string.split("-")[0]  # Eliminar el guión de la edad del jugador

    normalized_string = unicodedata.normalize('NFKD', string)
    string = normalized_string.encode('ASCII', 'ignore').decode('ASCII')

    return string


def getPlayers(url, team):
    print(f"EQUIPO: {team}")
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

    jugador = []
    tiempo_jugado = []
    rendimiento = []
    expectativa = []
    progresion = []
    por_90_minutos = []
    pertenece_a = []

    player_list = []

    for player_row in tbody_tr:
        player_str = ''
        player = {}

        # Obtener el nombre del jugador desde el <th>
        player_name_tag = player_row.find('th', {'data-stat': 'player'})
        if player_name_tag:
            player_str = player_name_tag.get_text(strip=True)
            player_str = player_str.lower()
            player_str = player_str.replace(".", "")  # Eliminar puntos
            player_str = clean_string(player_str)

        player['player'] = player_str

        # Obtener todos los datos desde los <td> con data-stat
        for data_cell in player_row.find_all('td', attrs={'data-stat': True}):
            stat = data_cell['data-stat']
            if stat == 'matches':
                break
            # print(stat)
            data = data_cell.get_text(strip=True)

            # Recuperando la nacionalidad en tres letras
            if stat == 'nationality':
                data = data[2:]  # Eliminando la nacionalidad repetida

            if stat == 'position':
                data = data.split(",")[0]  # Seleccionando la posición principal

            data = data.lower()
            data = clean_string(data)

            player[stat] = data if data else '0'

        player_list.append(player)

        team = team.lower()
        team = clean_string(team)

        # generar hechos de prolog
        try:
            jugador.append(
                f"jugador({player['player']}, {player['nationality']}, {player['position']}, {player['age']}).")

            tiempo_jugado.append(
                f"tiempo_jugado({player['player']}, {player['games']}, {player['games_starts']}, {player['minutes']}, {player['minutes_90s']}).")

            rendimiento.append(
                f"rendimiento({player['player']}, {player['goals']}, {player['assists']}, {player['goals_assists']}, {player['goals_pens']}, {player['pens_made']}, {player['pens_att']}, {player['cards_yellow']}, {player['cards_red']}).")

            expectativa.append(
                f"expectativa({player['player']}, {player['xg']}, {player['npxg']}, {player['xg_assist']}, {player['npxg_xg_assist']}).")

            progresion.append(
                f"progresion({player['player']}, {player['progressive_carries']}, {player['progressive_passes']}, {player['progressive_passes_received']}).")

            por_90_minutos.append(
                f"por_90_minutos({player['player']}, {player['goals_per90']}, {player['assists_per90']}, {player['goals_assists_per90']}, {player['goals_pens_per90']}, {player['goals_assists_pens_per90']}, {player['xg_per90']}, {player['xg_assist_per90']}, {player['xg_xg_assist_per90']}, {player['npxg_per90']}, {player['npxg_xg_assist_per90']}).")

            pertenece_a.append(f"pertenece_a({player['player']}, {team}).")

        except IndexError:
            pass

    return [jugador, tiempo_jugado, rendimiento, expectativa, progresion, por_90_minutos, pertenece_a]


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
    with open('ligamx.pl', 'w', encoding='utf-8') as file:
        file.write(':-style_check(-discontiguous).\n\n')

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
