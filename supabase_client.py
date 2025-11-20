"""Supabase client for fetching data"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

_client = None
_authenticated_client = None

def _get_client():
    """Get unauthenticated client (for reads)"""
    global _client
    if _client is None:
        _client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    return _client

def _get_authenticated_client():
    """Get authenticated client (for writes that require RLS)"""
    global _authenticated_client
    
    # Option 1: Use service role key if available (bypasses RLS)
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if service_role_key:
        if _authenticated_client is None:
            _authenticated_client = create_client(
                os.getenv("SUPABASE_URL"),
                service_role_key
            )
        return _authenticated_client
    
    # Option 2: Use authenticated session if available
    # Check if we have a session stored
    import streamlit as st
    session_data = st.session_state.get('supabase_session')
    if session_data:
        if _authenticated_client is None:
            _authenticated_client = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_KEY")
            )
            # Set the session with access token and refresh token
            _authenticated_client.auth.set_session(
                access_token=session_data.get('access_token'),
                refresh_token=session_data.get('refresh_token')
            )
        return _authenticated_client
    
    # Fallback: return regular client (will fail if RLS requires auth)
    return _get_client()

def authenticate_user(email: str, password: str):
    """Authenticate a user and store session"""
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.session:
            import streamlit as st
            # Store session data
            st.session_state['supabase_session'] = {
                'access_token': response.session.access_token,
                'refresh_token': response.session.refresh_token
            }
            st.session_state['supabase_user'] = response.user
            global _authenticated_client
            _authenticated_client = supabase
            return True, "Authentication successful"
        else:
            return False, "Authentication failed - no session returned"
    except Exception as e:
        return False, f"Authentication error: {str(e)}"

def fetch_data(table_name: str):
    """Fetch data from Supabase table"""
    supabase = _get_client()
    response = supabase.table(table_name).select("*").execute()
    return response.data or []

def fetch_particulars():
    """Fetch distinct particulars from the database"""
    try:
        supabase = _get_client()
        response = supabase.table('Particulars').select('*').execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Supabase error: {response.error}")
        
        if response.data and len(response.data) > 0:
            # Extract values from the 'Particulars' column (or any string column except 'id')
            particulars_list = []
            for item in response.data:
                if 'Particulars' in item:
                    value = item.get('Particulars')
                    if value:
                        particulars_list.append(str(value))
                else:
                    # Fallback: find any string column except 'id'
                    for key in item.keys():
                        value = item.get(key)
                        if value and isinstance(value, str) and key.lower() != 'id':
                            particulars_list.append(str(value))
                            break
            
            if particulars_list:
                return sorted(list(set(particulars_list)))
            else:
                return []
        else:
            return []
    except Exception as e:
        raise

def fetch_brands():
    """Fetch distinct brand names from the database"""
    try:
        supabase = _get_client()
        response = supabase.table('Brand').select('*').execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Supabase error: {response.error}")
        
        brands_list = []
        for item in response.data or []:
            if 'Brand' in item and item['Brand']:
                brands_list.append(str(item['Brand']))
            else:
                for key, value in item.items():
                    if key.lower() != 'id' and isinstance(value, str) and value:
                        brands_list.append(str(value))
                        break
        
        return sorted(set(brands_list))
    except Exception as e:
        raise

def fetch_brands_with_ids():
    """Fetch all brands with their IDs from the database"""
    try:
        supabase = _get_client()
        response = supabase.table('Brand').select('*').execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Supabase error: {response.error}")
        
        brands = []
        for item in response.data or []:
            brand_id = item.get('id') or item.get('Id') or item.get('ID')
            brand_name = None
            
            if 'Brand' in item and item['Brand']:
                brand_name = str(item['Brand'])
            else:
                for key, value in item.items():
                    if key.lower() != 'id' and isinstance(value, str) and value:
                        brand_name = str(value)
                        break
            
            if brand_id and brand_name:
                brands.append({
                    'id': brand_id,
                    'name': brand_name
                })
        
        return sorted(brands, key=lambda x: x['name'])
    except Exception as e:
        raise

def insert_driver(name: str, volt: int, watt: int, amp: float):
    """Insert a driver record into the Drivers table (requires authentication)"""
    try:
        supabase = _get_authenticated_client()
        response = supabase.table('Drivers').insert({
            'Name': name,
            'Volt': volt,
            'Watt': watt,
            'Amp': amp
        }).execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Supabase error: {response.error}")
        
        return response.data
    except Exception as e:
        raise

def insert_drivers_batch(drivers: list):
    """Insert multiple driver records into the Drivers table (requires authentication)"""
    try:
        supabase = _get_authenticated_client()
        response = supabase.table('Drivers').insert(drivers).execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Supabase error: {response.error}")
        
        return response.data
    except Exception as e:
        raise

def fetch_drivers():
    """Fetch all drivers from the Drivers table"""
    try:
        supabase = _get_client()
        response = supabase.table('Drivers').select('*').execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Supabase error: {response.error}")
        
        return response.data or []
    except Exception as e:
        raise