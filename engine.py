import os
from dotenv import load_dotenv
import requests


class ArbitrageEngine:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('API_KEY')
        self.base_url = 'https://api.the-odds-api.com/v4/sports/upcoming/odds'

        self.markets = {
            'Moneyline': 'h2h',
            #'Spread': 'spreads',
            #'Over/Under': 'totals'
        }
        self.default_market = 'Moneyline'

        self.regions = {
            'All': 'us,us2,uk,au,eu',
            'United States': 'us,us2',
            'United Kingdom': 'uk',
            'Australia': 'au',
            'European Union': 'eu'
        }
        self.default_region = 'All'

    def _calculate_matchup(self, matchup):
        optimal_outcomes = self._get_optimal_outcomes(matchup)
        arbitrage_details = self._get_arbitrage_details(optimal_outcomes)

        return {
            'sport_title': matchup['sport_title'],
            'commence_time': matchup['commence_time'],
            'optimal_outcomes': optimal_outcomes,
            'arbitrage_details': arbitrage_details
        }

    def _get_optimal_outcomes(self, matchup):
        optimal_outcomes = {}
        for bookmaker in matchup['bookmakers']:
            market = bookmaker['markets'][0] if bookmaker['markets'] else None
            if market:
                for outcome in market['outcomes']:
                    if not outcome['name'] in optimal_outcomes or outcome['price'] > optimal_outcomes[outcome['name']]['price']:
                        outcome['bookmaker'] = bookmaker['title']
                        outcome['link'] = bookmaker['link']
                        outcome['last_update'] = market['last_update']
                        optimal_outcomes[outcome['name']] = outcome
        return list(optimal_outcomes.values())

    def _get_arbitrage_details(self, outcomes):
        arbitrage_details = {}
        for outcome in outcomes:
            arbitrage_details[outcome['name']] = 1/outcome['price']
        arbitrage_details['total'] = sum(arbitrage_details.values())
        arbitrage_details['roi'] = 1/arbitrage_details['total'] - 1
        return arbitrage_details

    def search(self, market, region):
        url = f'{self.base_url}/?apiKey={self.api_key}&regions={self.regions[region]}&markets={self.markets[market]}&includeLinks=true&includeBetLimits=true'
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f'Error: {response.status_code}')
        data = response.json()
        
        # Overwrite sample_data.json with the raw API response
        # import json
        # with open('data/sample_h2h.json', 'w') as f:
        #     json.dump(data, f, indent=2)

        # Load sample_data.json
        # import json
        # with open('data/sample_h2h.json', 'r') as f:
        #     data = json.load(f)

        betting_matchups = [matchup for matchup in data if matchup.get('bookmakers')]
        results = [self._calculate_matchup(matchup) for matchup in betting_matchups]
        arbitrage_opportunities = list(filter(lambda x: x['arbitrage_details']['total'] < 1, results))

        return arbitrage_opportunities
