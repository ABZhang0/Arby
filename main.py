from engine import ArbitrageEngine
from nicegui import ui
from utils import format_timestamp, is_past_timestamp

engine = ArbitrageEngine()

results = []

def get_results(market, region):
    results.clear()
    results.extend(engine.search(market, region))
    results_ui.refresh()

@ui.refreshable
def results_ui():
    with ui.grid().classes('grid-cols-3 gap-4 w-full p-4'):
        for result in results:
            is_live = is_past_timestamp(result['commence_time'])
            with ui.card().classes('w-full'):
                bet_size = {'value': 100}

                with ui.row().classes('w-full justify-between items-start'):
                    with ui.column().classes('gap-0 mt-1 ml-2'):
                        ui.label(result['sport_title']).classes('font-medium text-2xl')
                        with ui.row().classes('items-center gap-2'):
                            ui.label(format_timestamp(result['commence_time'])).classes(
                                'text-base text-gray-400 ' + 
                                ('animate-pulse text-red-500' if is_live else '')
                            )
                            if is_live:
                                ui.label('LIVE').classes('text-sm bg-red-500 text-white px-1.5 py-0.5 rounded animate-pulse')
                    ui.label(format(result['arbitrage_details']['roi'], '.3%')).classes('number-font text-emerald-500 text-3xl font-medium bg-emerald-500/10 px-3 py-1 rounded-lg shadow-sm')

                ui.number(label='Bet Size', prefix='$', min=0, max=1000).bind_value(bet_size).classes('mx-auto text-lg number-font')
                ui.slider(min=0, max=1000).bind_value(bet_size).classes('mx-auto w-4/5 mb-4')

                with ui.row().classes('w-full gap-2'):
                    for outcome in result['optimal_outcomes']:
                        with ui.card().classes('flex-1'):
                            ui.label(outcome['name']).classes('text-center w-full font-medium text-lg mb-1')
                            ui.label(outcome['price']).classes('number-font text-center w-full text-2xl font-medium text-amber-400 mb-2')

                            with ui.row().classes('w-full justify-between items-center px-2 py-1 bg-white/5'):
                                ui.link(outcome['bookmaker'], outcome['link']).classes('text-sm font-medium hover:text-amber-400 transition-colors')
                                ui.label(format_timestamp(outcome['last_update'])).classes('text-xs text-gray-400')

                            with ui.card().classes('w-full'):
                                def get_stake(v, r, o):
                                    return v * r["arbitrage_details"][o["name"]]/r["arbitrage_details"]["total"]

                                with ui.timeline(side='right', color='green-800').classes('ml-2'):
                                    with ui.timeline_entry(subtitle='Stake', icon='attach_money').classes('-mb-5'):
                                        ui.label().bind_text_from(
                                            bet_size,
                                            'value',
                                            backward=lambda v, r=result, o=outcome: f'${(get_stake(v, r, o)):.2f}'
                                        ).classes('number-font font-medium -mt-5 text-right w-full -ml-4')
                                    
                                    with ui.timeline_entry(subtitle='Payout', icon='savings').classes('-mb-5'):
                                        ui.label().bind_text_from(
                                            bet_size,
                                            'value',
                                            backward=lambda v, r=result, o=outcome: f'${(get_stake(v, r, o) * o["price"]):.2f}'
                                        ).classes('number-font font-medium -mt-5 text-right w-full -ml-4')
                                    
                                    with ui.timeline_entry(subtitle='Profit', icon='trending_up').classes('-mb-5'):
                                        ui.label().bind_text_from(
                                            bet_size,
                                            'value',
                                            backward=lambda v, r=result, o=outcome: f'${(get_stake(v, r, o) * o["price"] - v):.2f}'
                                        ).classes('number-font font-medium -mt-5 text-right w-full -ml-4 text-lg text-emerald-500')

ui.colors(primary='#000000')
ui.query('body').classes('bg-emerald-900')

# Add Google Fonts links to the head
ui.add_head_html('''
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
''')

# Add custom CSS for fonts
ui.add_head_html('''
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
        .number-font {
            font-family: 'IBM Plex Mono', monospace;
            letter-spacing: -0.02em;  /* Slightly tighter spacing for numbers */
        }
    </style>
''')

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

ui.run(title='Arby')
