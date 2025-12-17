"""Supabase client for fetching data"""

import os
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

_client = None
_authenticated_client = None

def _get_env_var(key: str):
    """Get environment variable from Streamlit secrets or os.environ"""
    try:
        import streamlit as st
        from streamlit.errors import StreamlitSecretNotFoundError
        # Try Streamlit secrets first (for Streamlit Cloud)
        try:
            if hasattr(st, 'secrets') and st.secrets is not None:
                # Check if key exists in secrets (handles both dict-like and object-like access)
                try:
                    if key in st.secrets:
                        return st.secrets[key]
                except (TypeError, AttributeError):
                    # If secrets is not dict-like, try attribute access
                    if hasattr(st.secrets, key):
                        return getattr(st.secrets, key)
        except StreamlitSecretNotFoundError:
            # Secrets file doesn't exist, fall through to os.environ
            pass
        except (KeyError, AttributeError):
            # Key doesn't exist in secrets, fall through to os.environ
            pass
    except (AttributeError, RuntimeError, ImportError):
        # Not in Streamlit context or secrets not available
        pass
    
    # Fallback to os.environ (for local development with .env file)
    return os.getenv(key)

def _validate_env_vars():
    """Validate that required environment variables are set"""
    supabase_url = _get_env_var("SUPABASE_URL")
    supabase_key = _get_env_var("SUPABASE_KEY")
    
    if not supabase_url:
        raise ValueError(
            "SUPABASE_URL is not configured. "
            "For local development: Create a .env file with SUPABASE_URL=your-url. "
            "For Streamlit Cloud: Add SUPABASE_URL to your app's Secrets (Settings → Secrets). "
            "See README.md for setup instructions."
        )
    if not supabase_key:
        raise ValueError(
            "SUPABASE_KEY is not configured. "
            "For local development: Create a .env file with SUPABASE_KEY=your-key. "
            "For Streamlit Cloud: Add SUPABASE_KEY to your app's Secrets (Settings → Secrets). "
            "See README.md for setup instructions."
        )
    
    # Validate URL format
    if not supabase_url.startswith(('http://', 'https://')):
        raise ValueError(
            f"SUPABASE_URL must start with http:// or https://. "
            f"Current value appears to be invalid. "
            f"Expected format: https://ldatmittxoudwpcgdcbc.supabase.co"
        )
    
    return supabase_url, supabase_key

def check_supabase_config():
    """Public function to check if Supabase is configured"""
    try:
        _validate_env_vars()
        return True, None
    except ValueError as e:
        return False, str(e)

def test_supabase_connection():
    """Test the Supabase connection and return diagnostic information"""
    try:
        supabase_url, supabase_key = _validate_env_vars()
        
        # Extract hostname for DNS test
        import re
        url_match = re.search(r'https?://([^/]+)', supabase_url)
        hostname = url_match.group(1) if url_match else None
        
        # Try to create client and make a simple request
        try:
            client = create_client(supabase_url, supabase_key)
            # Try a simple query to test connection
            response = client.table('Particulars').select('*').limit(1).execute()
            return True, f"Connection successful to {hostname}"
        except Exception as e:
            error_msg = str(e)
            if "Name or service not known" in error_msg or "[Errno -2]" in error_msg:
                return False, f"DNS resolution failed for hostname '{hostname}'. Check your SUPABASE_URL."
            return False, f"Connection failed: {error_msg}"
    except ValueError as e:
        return False, f"Configuration error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def _get_client():
    """Get unauthenticated client (for reads)"""
    global _client
    if _client is None:
        supabase_url, supabase_key = _validate_env_vars()
        try:
            _client = create_client(supabase_url, supabase_key)
        except Exception as e:
            # Provide more helpful error messages for common issues
            error_msg = str(e)
            if "Name or service not known" in error_msg or "[Errno -2]" in error_msg:
                # Extract hostname from URL for better error message
                import re
                url_match = re.search(r'https?://([^/]+)', supabase_url)
                hostname = url_match.group(1) if url_match else "unknown"
                raise ConnectionError(
                    f"DNS resolution failed for Supabase hostname '{hostname}'. "
                    f"Please check:\n"
                    f"1. Your SUPABASE_URL is correct (should be like: https://xxxxx.supabase.co)\n"
                    f"2. Your internet connection is working\n"
                    f"3. The Supabase project is active and accessible\n"
                    f"Original error: {error_msg}"
                )
            raise
    return _client

def _get_authenticated_client():
    """Get authenticated client (for writes that require RLS)"""
    global _authenticated_client
    
    supabase_url, supabase_key = _validate_env_vars()
    
    # Option 1: Use service role key if available (bypasses RLS)
    service_role_key = _get_env_var("SUPABASE_SERVICE_ROLE_KEY")
    if service_role_key:
        if _authenticated_client is None:
            _authenticated_client = create_client(supabase_url, service_role_key)
        return _authenticated_client
    
    # Option 2: Use authenticated session if available
    # Check if we have a session stored
    import streamlit as st
    session_data = st.session_state.get('supabase_session')
    if session_data:
        if _authenticated_client is None:
            _authenticated_client = create_client(supabase_url, supabase_key)
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
        supabase_url, supabase_key = _validate_env_vars()
        supabase = create_client(supabase_url, supabase_key)
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
    except ValueError as e:
        # Environment variable validation error
        return False, str(e)
    except Exception as e:
        return False, f"Authentication error: {str(e)}"

def fetch_data(table_name: str):
    """Fetch data from Supabase table"""
    supabase = _get_client()
    response = supabase.table(table_name).select("*").execute()
    return response.data or []

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes, hide spinner
def fetch_particulars():
    """Fetch distinct particulars from the database"""
    try:
        supabase = _get_client()
        # Use select('*') to handle different column name variations
        # The fallback logic below will find the correct column
        response = supabase.table('Particulars').select('*').execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Supabase error: {response.error}")
        
        if response.data and len(response.data) > 0:
            # Extract values from the 'Particulars' column (or fallback to any string column)
            particulars_list = []
            for item in response.data:
                # Try common column name variations
                if 'Particulars' in item:
                    value = item.get('Particulars')
                    if value:
                        particulars_list.append(str(value))
                elif 'particulars' in item:
                    value = item.get('particulars')
                    if value:
                        particulars_list.append(str(value))
                elif 'name' in item:
                    value = item.get('name')
                    if value:
                        particulars_list.append(str(value))
                elif 'Name' in item:
                    value = item.get('Name')
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

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes, hide spinner
def fetch_brands():
    """Fetch distinct brand names from the database"""
    try:
        supabase = _get_client()
        # Use select('*') to handle different column name variations
        # The fallback logic below will find the correct column
        response = supabase.table('Brand').select('*').execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Supabase error: {response.error}")
        
        brands_list = []
        for item in response.data or []:
            # Try common column name variations
            if 'Brand' in item and item['Brand']:
                brands_list.append(str(item['Brand']))
            elif 'brand' in item and item['brand']:
                brands_list.append(str(item['brand']))
            elif 'name' in item and item['name']:
                brands_list.append(str(item['name']))
            elif 'Name' in item and item['Name']:
                brands_list.append(str(item['Name']))
            else:
                # Fallback: find any string column except 'id'
                for key, value in item.items():
                    if key.lower() != 'id' and isinstance(value, str) and value:
                        brands_list.append(str(value))
                        break
        
        return sorted(set(brands_list))
    except Exception as e:
        raise

@st.cache_data(ttl=300)  # Cache for 5 minutes
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

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes, hide spinner
def fetch_drivers(location_type: str = "both"):
    """Fetch drivers from the Drivers table, filtered by location type if specified"""
    try:
        supabase = _get_client()
        # Select only needed columns for better performance, including Place column
        response = supabase.table('Drivers').select('Name,Volt,Watt,Amp,Price,Bid,Place').execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Supabase error: {response.error}")
        
        all_drivers = response.data or []
        
        # Filter by location type if not "both" (case-insensitive matching)
        if location_type == "both":
            return all_drivers
        
        # Filter drivers by Place column (case-insensitive)
        filtered_drivers = []
        location_type_lower = location_type.lower()
        
        for driver in all_drivers:
            driver_place = driver.get('Place') or driver.get('place') or ''
            # Case-insensitive comparison
            if driver_place.lower() == location_type_lower:
                filtered_drivers.append(driver)
        
        return filtered_drivers
    except Exception as e:
        raise