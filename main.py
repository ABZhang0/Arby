import os
from dotenv import load_dotenv
import requests


load_dotenv()
API_KEY = os.getenv('API_KEY')


def calculate_matchup(matchup):
    optimal_outcomes = get_optimal_outcomes(matchup)
    arbitrage_details = get_arbitrage_details(optimal_outcomes)

    return {
        'sport_title': matchup['sport_title'],
        'commence_time': matchup['commence_time'],
        'optimal_outcomes': optimal_outcomes,
        'arbitrage_details': arbitrage_details
    }


def get_optimal_outcomes(matchup):
    optimal_outcomes = {}
    for bookmaker in matchup['bookmakers']:
        # TODO: handle other markets (e.g. spreads)
        h2h_market = next(m for m in bookmaker['markets'] if m['key'] == 'h2h')
        for outcome in h2h_market['outcomes']:
            if not outcome['name'] in optimal_outcomes or outcome['price'] > optimal_outcomes[outcome['name']]['price']:
                outcome['bookmaker'] = bookmaker['key']
                outcome['last_update'] = h2h_market['last_update']
                optimal_outcomes[outcome['name']] = outcome
    return list(optimal_outcomes.values())


def get_arbitrage_details(outcomes):
    arbitrage_details = {}
    for outcome in outcomes:
        arbitrage_details[outcome['name']] = 1/outcome['price']
    arbitrage_details['total'] = sum(arbitrage_details.values())
    return arbitrage_details


try:
    url = f'https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={API_KEY}&regions=us,us2,uk,au,eu'
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f'Error: {response.status_code}')
    data = response.json()

    results = [calculate_matchup(matchup) for matchup in data]
    arbitrage_opportunities = list(filter(lambda x: x['arbitrage_details']['total'] < 1, results))

    import json
    print(json.dumps(arbitrage_opportunities, indent=4))
except Exception as e:
    print(repr(e))
