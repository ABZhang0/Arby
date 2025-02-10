from search import search
from nicegui import ui
from datetime import datetime, timezone


def format_timestamp(timestamp):
    return datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%m/%d/%Y %H:%M')

results = []

@ui.refreshable
def results_ui():
    for result in results:
        with ui.card():
            bet_size = {'value': 100}

            with ui.row():
                ui.label(result['sport_title'])
                ui.label(format(1-result['arbitrage_details']['total'], '.3%'))
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
                            ui.label().bind_text_from(
                                bet_size,
                                'value',
                                backward=lambda v, r=result, o=outcome: f'Bet Amount: ${(v * r["arbitrage_details"][o["name"]]):.2f}'
                            )
                            ui.label().bind_text_from(
                                bet_size,
                                'value',
                                backward=lambda v, r=result, o=outcome: f'Profit: ${(v * r["arbitrage_details"][o["name"]] - v):.2f}'
                            )


def get_results():
    results.clear()
    results.extend(search())
    results_ui.refresh()


ui.label('Arby')
ui.button('Search', on_click=lambda: get_results())
results_ui()

ui.run()
