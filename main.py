from engine import ArbitrageEngine
from nicegui import ui
from utils import format_timestamp

engine = ArbitrageEngine()

results = []

def get_results(market, region):
    results.clear()
    results.extend(engine.search(market, region))
    results_ui.refresh()

@ui.refreshable
def results_ui():
    for result in results:
        with ui.card():
            bet_size = {'value': 100}

            with ui.row():
                ui.label(result['sport_title'])
                ui.label(format(result['arbitrage_details']['roi'], '.3%'))
            ui.label(format_timestamp(result['commence_time']))
            ui.slider(min=0, max=1000).bind_value(bet_size)
            ui.number().bind_value(bet_size)

            with ui.row():
                for outcome in result['optimal_outcomes']:
                    with ui.card():
                        ui.label(outcome['name'])
                        ui.label(outcome['price'])

                        with ui.row():
                            ui.label(outcome['bookmaker'])
                            ui.label(format_timestamp(outcome['last_update']))

                        with ui.card():
                            def get_stake(v, r, o):
                                return v * r["arbitrage_details"][o["name"]]/r["arbitrage_details"]["total"]

                            ui.label().bind_text_from(
                                bet_size,
                                'value',
                                backward=lambda v, r=result, o=outcome: f'Stake: ${(get_stake(v, r, o)):.2f}'
                            )
                            ui.label().bind_text_from(
                                bet_size,
                                'value',
                                backward=lambda v, r=result, o=outcome: f'Payout: ${(get_stake(v, r, o) * o["price"]):.2f}'
                            )
                            ui.label().bind_text_from(
                                bet_size,
                                'value',
                                backward=lambda v, r=result, o=outcome: f'Profit: ${(get_stake(v, r, o) * o["price"] - v):.2f}'
                            )

ui.query('body').classes('bg-emerald-900')

with ui.header().classes('w-full flex justify-between items-center p-0 bg-emerald-800 shadow-lg shadow-black/50'):
    # Left side - logo
    with ui.element('div').classes('flex items-start gap-2 h-full mt-1 ml-1'):
        with open('assets/logo.svg', 'r') as f:
            svg_content = f.read()
        ui.html(svg_content)
    
    # Right side - controls
    with ui.element('div').classes('flex items-center gap-8 mr-12'):
        market_dropdown = ui.select(
            list(engine.markets.keys()), 
            label='Market', 
            value=engine.default_market
        ).classes('text-xl w-48')
        region_dropdown = ui.select(
            list(engine.regions.keys()), 
            label='Location', 
            value=engine.default_region
        ).classes('text-xl w-48')
        ui.button(
            'Search', 
            on_click=lambda: get_results(market=market_dropdown.value, region=region_dropdown.value)
        ).classes('text-xl font-bold px-8 py-2 rounded-full shadow-lg transform hover:scale-105 transition-all duration-200')

results_ui()

ui.run()
