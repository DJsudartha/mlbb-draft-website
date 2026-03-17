import requests
from bs4 import BeautifulSoup

liquipedia_base_url = 'https://liquipedia.net/mobilelegends/'
mlbb_official_base_url = 'https://www.mobilelegends.com/en/hero-stats'
DEFAULT_TOURNAMENT_NAME = "M7_World_Championship"
DEFAULT_STAGE = "Knockout_Stage"

# Function to scrape hero data from Liquipedia by giving the tournament's name
def get_liquipedia_hero_data(tournament_name, stage=""):
    split_name = tournament_name.split()
    url_name = '/'.join(split_name)
    new_url = liquipedia_base_url + url_name + '/Statistics' + (f'/{stage}' if stage else '')      
    print(f"Scraping data from: {new_url}")
    res = requests.get(new_url)

    if res.status_code != 200:
        print(f"Failed to retrieve data from {new_url}")
        return {}
    
    soup = BeautifulSoup(res.content, 'html.parser')
    hero_data = {}

    s = soup.find_all('tr', class_='character-stats-row')
    for row in s:
        columns = row.find_all('td')
        hero = columns[1].find_all('a')[1].text.strip()
        picks = columns[2].text.strip()
        wins = columns[3].text.strip()
        losses = columns[4].text.strip()
        win_rate = columns[5].text.strip()
        pick_rate = columns[6].text.strip()
        bans = columns[15].text.strip()
        ban_rate = columns[16].text.strip()
        presence_count = columns[17].text.strip()
        presence_rate = columns[18].text.strip()
        hero_data[hero] = {
            'picks': picks,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'pick_rate': pick_rate,
            'bans': bans,
            'ban_rate': ban_rate,
            'presence_count': presence_count,
            'presence_rate': presence_rate,
        }
    return hero_data
    

if __name__ == "__main__":
    tournament_name = DEFAULT_TOURNAMENT_NAME
    hero_data = get_liquipedia_hero_data(tournament_name, DEFAULT_STAGE)
    for hero, stats in hero_data.items():
        print(
            f"{hero}: Picks: {stats['picks']}, Pick Rate: {stats['pick_rate']}, "
            f"Win Rate: {stats['win_rate']}, Ban Rate: {stats['ban_rate']}"
        )
