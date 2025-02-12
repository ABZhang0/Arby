from datetime import datetime, timezone
import requests

def format_timestamp(timestamp):
    return datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%m/%d %H:%M:%S')

def is_past_timestamp(timestamp):
    timestamp_dt = datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc)
    current_dt = datetime.now(timezone.utc)
    return timestamp_dt < current_dt

def get_user_us_state(default_state = 'NJ'):
    try:
        response = requests.get('https://ipapi.co/json/')
        if response.status_code != 200:
            raise Exception(response.reason)
        data = response.json()
        
        if data.get('country_code') != 'US':
            return default_state
        
        state = data.get('region_code')
        return state if state else default_state
        
    except Exception as e:
        print(f"Error detecting location: {e}")
        return default_state
    
def get_us_states():
    return [
        'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 
        'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
        'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'
    ]
