"""Driver form component"""

import streamlit as st
import pandas as pd
from config import VOLTAGE_OPTIONS, LED_OPTIONS
from utils import calculate_wattage
from supabase_client import fetch_drivers


def _parse_editing_row():
    """Parse editing row data to get default values"""
    defaults = ("", False, 0, 0, "0")
    if not st.session_state.editing_row:
        return defaults
    
    row = st.session_state.editing_row
    length_str = row.get("Length", "")
    default_length = ""
    default_is_feet = False
    
    if length_str:
        parts = length_str.split()
        if len(parts) >= 2:
            default_length = parts[0]
            default_is_feet = parts[1].lower() == "feet"
    
    try:
        voltage_val = int(row.get("Voltage", "").replace("V", ""))
        default_voltage_index = VOLTAGE_OPTIONS.index(voltage_val) if voltage_val in VOLTAGE_OPTIONS else 0
    except:
        default_voltage_index = 0
    
    led_val = row.get("LED", "")
    default_led_index = LED_OPTIONS.index(led_val) if led_val in LED_OPTIONS else 0
    
    default_discount = row.get("Discount", "0")
    if default_discount == "-":
        default_discount = "0"
    
    return default_length, default_is_feet, default_voltage_index, default_led_index, default_discount


def _convert_and_calculate(length, unit, led_count):
    """Convert feet to meters if needed and calculate wattage."""
    converted_length = round(length * 0.3048, 2) if unit == "Feet" else length
    wattage = calculate_wattage(converted_length, led_count, "Meter")
    return converted_length, "Meter", wattage


def _find_nearest_driver(drivers, calculated_wattage, voltage):
    """Find the nearest driver that is equal to or above the calculated wattage and matches voltage"""
    if not drivers:
        return None, None
    
    nearest_driver = None
    min_diff = float('inf')
    
    for driver in drivers:
        driver_watt = driver.get('Watt') or driver.get('watt') or 0
        driver_volt = driver.get('Volt') or driver.get('volt') or 0
        
        # Only consider drivers that match voltage AND are equal to or above the calculated wattage
        if driver_volt == voltage and driver_watt >= calculated_wattage:
            # Calculate wattage difference (positive, since driver_watt >= calculated_wattage)
            watt_diff = driver_watt - calculated_wattage
            
            if watt_diff < min_diff:
                min_diff = watt_diff
                nearest_driver = driver
    
    return nearest_driver, min_diff


def _filter_nearby_drivers(drivers, calculated_wattage, voltage, max_percentage_diff=50):
    """Filter drivers to show only those equal to or above the calculated wattage and matching voltage"""
    if not drivers:
        return []
    
    nearby_drivers = []
    
    for driver in drivers:
        driver_watt = driver.get('Watt') or driver.get('watt') or 0
        driver_volt = driver.get('Volt') or driver.get('volt') or 0
        
        # Only include drivers that match the selected voltage AND are equal to or above the calculated wattage
        if driver_volt == voltage and driver_watt >= calculated_wattage:
            # Calculate percentage difference (only for drivers above)
            if calculated_wattage > 0:
                percentage_diff = ((driver_watt - calculated_wattage) / calculated_wattage) * 100
            else:
                percentage_diff = float('inf')
            
            # Include drivers within the percentage threshold (above the calculated wattage)
            if percentage_diff <= max_percentage_diff:
                watt_diff = driver_watt - calculated_wattage  # Positive difference (above)
                
                nearby_drivers.append({
                    'driver': driver,
                    'watt_diff': watt_diff,
                    'percentage_diff': percentage_diff,
                    'driver_watt': driver_watt
                })
    
    # Sort by wattage difference (closest above first)
    nearby_drivers.sort(key=lambda x: x['watt_diff'])
    
    return [item['driver'] for item in nearby_drivers]


def _find_driver_combinations(drivers, calculated_wattage, voltage, location_type="both", single_driver_available=False, max_combinations=3, tolerance_percent=10):
    """Find combinations of drivers that sum up to near the calculated wattage, considering cost efficiency and location type"""
    if not drivers or calculated_wattage <= 0:
        return []
    
    # Filter drivers with matching voltage, location type, and reasonable wattage
    candidate_drivers = []
    location_type_lower = location_type.lower() if location_type else "both"
    
    for driver in drivers:
        driver_watt = driver.get('Watt') or driver.get('watt') or 0
        driver_volt = driver.get('Volt') or driver.get('volt') or 0
        driver_price = driver.get('Price') or driver.get('price') or 0
        driver_place = driver.get('Place') or driver.get('place') or ''
        
        # Check if location type matches (if not "both")
        location_matches = True
        if location_type_lower != "both":
            driver_place_lower = driver_place.lower() if driver_place else ''
            location_matches = driver_place_lower == location_type_lower
        
        # Only consider drivers with matching voltage, matching location type, and positive wattage
        if driver_volt == voltage and driver_watt > 0 and location_matches:
            candidate_drivers.append({
                'driver': driver,
                'watt': driver_watt,
                'price': driver_price
            })
    
    if not candidate_drivers:
        return []
    
    combinations = []
    tolerance = calculated_wattage * (tolerance_percent / 100)
    max_watt = calculated_wattage * 1.15   # Allow up to 15% over
    
    # If single driver is available, only show combinations if they're significantly better
    # (e.g., much closer match or significantly cheaper)
    # Otherwise, show combinations as alternatives
    
    # Find combinations of 2 drivers
    for i in range(len(candidate_drivers)):
        for j in range(i + 1, len(candidate_drivers)):
            total_watt = candidate_drivers[i]['watt'] + candidate_drivers[j]['watt']
            
            # Only include combinations that are equal to or above the calculated wattage
            if total_watt >= calculated_wattage:
                diff = total_watt - calculated_wattage  # Positive difference (above)
                
                # Include if within tolerance (up to 15% over)
                if diff <= tolerance or total_watt <= max_watt:
                    total_price = candidate_drivers[i]['price'] + candidate_drivers[j]['price']
                    
                    # If single driver available, only show 2-driver combo if:
                    # 1. It's a much better match (within 5% vs single driver being >10% over)
                    # 2. OR it's significantly cheaper (at least 20% cheaper)
                    # 3. OR single driver doesn't exist for this wattage range
                    if single_driver_available:
                        # Check if this combination makes sense
                        # For now, allow it if it's a good match (within 10%)
                        if diff <= calculated_wattage * 0.10:
                            combinations.append({
                                'drivers': [candidate_drivers[i]['driver'], candidate_drivers[j]['driver']],
                                'watts': [candidate_drivers[i]['watt'], candidate_drivers[j]['watt']],
                                'total_watt': total_watt,
                                'diff': diff,
                                'percentage_diff': (diff / calculated_wattage * 100) if calculated_wattage > 0 else 0,
                                'total_price': total_price,
                                'driver_count': 2
                            })
                    else:
                        # No single driver available, show combination
                        combinations.append({
                            'drivers': [candidate_drivers[i]['driver'], candidate_drivers[j]['driver']],
                            'watts': [candidate_drivers[i]['watt'], candidate_drivers[j]['watt']],
                            'total_watt': total_watt,
                            'diff': diff,
                            'percentage_diff': (diff / calculated_wattage * 100) if calculated_wattage > 0 else 0,
                            'total_price': total_price,
                            'driver_count': 2
                        })
    
    # Only find combinations of 3 drivers if no single driver is available
    # OR if calculated wattage is very high (e.g., >500W) where 3 drivers might make sense
    if not single_driver_available or calculated_wattage > 500:
        if len(candidate_drivers) >= 3:
            for i in range(len(candidate_drivers)):
                for j in range(i + 1, len(candidate_drivers)):
                    for k in range(j + 1, len(candidate_drivers)):
                        total_watt = (candidate_drivers[i]['watt'] + 
                                     candidate_drivers[j]['watt'] + 
                                     candidate_drivers[k]['watt'])
                        
                        # Only include combinations that are equal to or above the calculated wattage
                        if total_watt >= calculated_wattage:
                            diff = total_watt - calculated_wattage  # Positive difference (above)
                            
                            # Only show 3-driver combinations if they're very close match (within 5%)
                            # and wattage is high enough to justify multiple drivers
                            if diff <= calculated_wattage * 0.05 and total_watt <= max_watt:
                                total_price = candidate_drivers[i]['price'] + candidate_drivers[j]['price'] + candidate_drivers[k]['price']
                                
                                combinations.append({
                                    'drivers': [
                                        candidate_drivers[i]['driver'],
                                        candidate_drivers[j]['driver'],
                                        candidate_drivers[k]['driver']
                                    ],
                                    'watts': [
                                        candidate_drivers[i]['watt'],
                                        candidate_drivers[j]['watt'],
                                        candidate_drivers[k]['watt']
                                    ],
                                    'total_watt': total_watt,
                                    'diff': diff,
                                    'percentage_diff': (diff / calculated_wattage * 100) if calculated_wattage > 0 else 0,
                                    'total_price': total_price,
                                    'driver_count': 3
                                })
    
    # Sort by: 1) driver count (fewer first), 2) difference (best match), 3) price (cheaper first)
    combinations.sort(key=lambda x: (x['driver_count'], x['diff'], x['total_price']))
    
    # Limit to top combinations
    return combinations[:max_combinations]


def render_driver_form(brand_name, location_type):
    """Render the driver form with all inputs and buttons"""
    default_length, default_is_feet, default_voltage_index, default_led_index, default_discount = _parse_editing_row()
    
    # Use defaults if editing row, otherwise use session state (widgets with keys persist automatically)
    if st.session_state.editing_row is not None:
        form_length = default_length
        form_voltage_index = default_voltage_index
        form_led_index = default_led_index
        form_discount = default_discount
    else:
        # Initialize with defaults if not in session state
        form_length = st.session_state.get("form_length_input", default_length if default_length else "")
        form_voltage_index = st.session_state.get("form_voltage_index", default_voltage_index)
        form_led_index = st.session_state.get("form_led_count_index", default_led_index)
        form_discount = st.session_state.get("form_discount_input", default_discount if default_discount else "")
    
    current_is_feet = default_is_feet if st.session_state.editing_row is not None else st.session_state.get("unit_toggle", False)
    toggle_label = "Feet" if current_is_feet else "Meter"
    
    col_length, col_unit_toggle = st.columns(2)
    with col_length:
        length_input = st.text_input(
            f"📏 Length ({toggle_label})", 
            value=form_length, 
            placeholder=f"Enter length in {toggle_label.lower()}",
            key="form_length_input",
            help=f"Enter the length of the LED strip in {toggle_label.lower()}"
        )
    with col_unit_toggle:
        st.markdown('<div style="display: flex; align-items: center; height: 100%; padding-top: 1.5rem;">', unsafe_allow_html=True)
        is_feet = st.toggle(
            "Switch to Feet" if not current_is_feet else "Switch to Meter", 
            value=current_is_feet, 
            key="unit_toggle",
            help="Toggle between Feet and Meter units"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    unit = "Feet" if is_feet else "Meter"
    
    try:
        length = int(length_input) if length_input else None
        if length is not None and length < 0:
            st.warning("⚠️ Length must be a positive integer")
            length = None
    except ValueError:
        if length_input:  # Only show warning if user entered something
            st.warning("⚠️ Please enter a valid integer for length")
        length = None
    
    col_voltage, col_led = st.columns(2)
    with col_voltage:
        # Get current index from session state if available
        if "form_voltage" in st.session_state:
            current_voltage = st.session_state.form_voltage
            if current_voltage in VOLTAGE_OPTIONS:
                form_voltage_index = VOLTAGE_OPTIONS.index(current_voltage)
            else:
                form_voltage_index = default_voltage_index
        voltage = st.selectbox(
            "⚡ Voltage (V)", 
            VOLTAGE_OPTIONS, 
            index=form_voltage_index,
            key="form_voltage",
            help="Select the voltage rating for your LED strip"
        )
    with col_led:
        # Get current index from session state if available
        if "form_led_count" in st.session_state:
            current_led = st.session_state.form_led_count
            if current_led in LED_OPTIONS:
                form_led_index = LED_OPTIONS.index(current_led)
            else:
                form_led_index = default_led_index
        led_count = st.selectbox(
            "💡 LED Count per Meter", 
            LED_OPTIONS, 
            index=form_led_index,
            key="form_led_count",
            help="Select the number of LEDs per meter"
        )
    
    discount = st.text_input(
        "💰 Discount (%)", 
        value=form_discount, 
        placeholder="Enter discount percentage (optional)",
        key="form_discount_input",
        help="Optional: Enter discount percentage if applicable"
    )
    
    # Calculate button
    calculate_clicked = st.button("🧮 Calculate Wattage", type="primary", key="calc_btn", use_container_width=True)
    
    def _is_valid_input():
        return length is not None and length > 0 and led_count > 0
    
    def _get_calculation():
        """Get calculation, using cache if available."""
        cache = st.session_state
        if (cache.get('calculated_wattage') and 
            cache.get('calc_length') == length and
            cache.get('calc_led_count') == led_count and
            cache.get('calc_unit') == unit):
            return cache.calc_converted_length, "Meter", cache.calculated_wattage
        return _convert_and_calculate(length, unit, led_count)
    
    # Check if we should show driver options (either just calculated or calculation state exists)
    should_show_drivers = False
    cached_wattage = None
    cached_voltage = None
    
    if calculate_clicked and _is_valid_input():
        calc_length, _, wattage = _convert_and_calculate(length, unit, led_count)
        
        # Display calculation result
        st.success(f"✨ **{wattage} W**")
        
        st.session_state.update({
            'calculated_wattage': wattage,
            'calc_length': length,
            'calc_led_count': led_count,
            'calc_unit': unit,
            'calc_converted_length': calc_length,
            'calc_voltage': voltage
        })
        should_show_drivers = True
        cached_wattage = wattage
        cached_voltage = voltage
    elif st.session_state.get('calculated_wattage') and _is_valid_input():
        # Show drivers if calculation state exists and inputs are still valid
        cached_wattage = st.session_state.calculated_wattage
        cached_voltage = st.session_state.get('calc_voltage', voltage)
        # Show cached calculation result (only show once, not on every rerun)
        calc_length = st.session_state.get('calc_converted_length', 0)
        cached_led = st.session_state.get('calc_led_count', led_count)
        # Don't show the message again - user already saw it when they clicked Calculate
        should_show_drivers = True
    
    if should_show_drivers:
        # Fetch drivers from database and show nearby drivers
        try:
            with st.spinner("Fetching drivers from database..."):
                all_drivers = fetch_drivers(location_type)
            
            if all_drivers:
                # Filter to show only nearby drivers (within 50% of calculated wattage)
                nearby_drivers = _filter_nearby_drivers(all_drivers, cached_wattage, cached_voltage, max_percentage_diff=50)
                
                if nearby_drivers:
                    nearest_driver, diff = _find_nearest_driver(nearby_drivers, cached_wattage, cached_voltage)
                    
                    st.markdown(f"<h4 style='font-size: 1rem; margin-bottom: 0.5rem;'>📋 Available Drivers & Combinations ({cached_voltage}V)</h4>", unsafe_allow_html=True)
                    st.caption("Select a driver option below and add it to your table")
                    
                    # Prepare combined data for display
                    all_options_data = []
                    
                    # Add single drivers
                    for driver in nearby_drivers:
                        driver_watt = driver.get('Watt') or driver.get('watt') or 0
                        driver_volt = driver.get('Volt') or driver.get('volt') or 0
                        driver_amp = driver.get('Amp') or driver.get('amp') or 0
                        driver_name = driver.get('Name') or driver.get('name') or '-'
                        driver_price = driver.get('Price') or driver.get('price')
                        
                        is_nearest = driver == nearest_driver
                        watt_diff = driver_watt - cached_wattage
                        
                        all_options_data.append({
                            'Type': '1',
                            'Name/Combination': f"{driver_name} ({driver_watt}W)",
                            'Wattage': f"{driver_watt}W",
                            'Volt': f"{driver_volt}V",
                            'Amp': f"{driver_amp}A",
                            'Price': f"₹{driver_price}" if driver_price else '-',
                            'Best': '⭐' if is_nearest else '',
                            '_sort_diff': watt_diff  # Hidden field for sorting
                        })
                    
                    # Find and add driver combinations
                    # Filter by voltage and location type (place)
                    location_type_lower = location_type.lower() if location_type else "both"
                    matching_voltage_drivers = []
                    for d in all_drivers:
                        driver_volt = d.get('Volt') or d.get('volt') or 0
                        driver_place = d.get('Place') or d.get('place') or ''
                        
                        # Check voltage match
                        voltage_matches = driver_volt == cached_voltage
                        
                        # Check location type match (if not "both")
                        location_matches = True
                        if location_type_lower != "both":
                            driver_place_lower = driver_place.lower() if driver_place else ''
                            location_matches = driver_place_lower == location_type_lower
                        
                        if voltage_matches and location_matches:
                            matching_voltage_drivers.append(d)
                    
                    # Check if single driver is available
                    single_driver_available = len(nearby_drivers) > 0
                    
                    if matching_voltage_drivers:
                        combinations = _find_driver_combinations(
                            matching_voltage_drivers, 
                            cached_wattage, 
                            cached_voltage,
                            location_type,
                            single_driver_available=single_driver_available,
                            max_combinations=5
                        )
                        
                        for idx, combo in enumerate(combinations, 1):
                            driver_names = []
                            driver_watts = []
                            total_price = 0
                            total_volt = None
                            total_amp = 0
                            
                            combination_parts = []
                            for driver in combo['drivers']:
                                driver_name = driver.get('Name') or driver.get('name') or '-'
                                driver_watt = driver.get('Watt') or driver.get('watt') or 0
                                driver_volt = driver.get('Volt') or driver.get('volt') or 0
                                driver_amp = driver.get('Amp') or driver.get('amp') or 0
                                driver_price = driver.get('Price') or driver.get('price') or 0
                                
                                combination_parts.append(f"{driver_name} ({driver_watt}W)")
                                total_price += driver_price
                                if total_volt is None:
                                    total_volt = driver_volt
                                total_amp += driver_amp
                            
                            all_options_data.append({
                                'Type': str(len(combo["drivers"])),
                                'Name/Combination': " + ".join(combination_parts),
                                'Wattage': f"{combo['total_watt']:.2f}W",
                                'Volt': f"{total_volt}V",
                                'Amp': f"{total_amp:.2f}A",
                                'Price': f"₹{total_price:.2f}" if total_price > 0 else '-',
                                'Best': '🏆' if idx == 1 else '',
                                '_sort_diff': combo['diff']  # Hidden field for sorting
                            })
                    
                    # Sort by difference (best matches first)
                    all_options_data.sort(key=lambda x: x['_sort_diff'])
                    
                    # Display custom table with buttons
                    st.markdown("<h4 style='font-size: 1rem; margin-bottom: 0.5rem;'>🎯 Driver Options</h4>", unsafe_allow_html=True)
                    
                    # Display each row with button - responsive widths
                    for idx, option in enumerate(all_options_data):
                        row_cols = st.columns([0.3, 2.5, 0.5, 0.5, 0.5, 0.7, 0.3, 0.5], gap="small")
                        
                        with row_cols[0]:
                            st.markdown(f"<div style='font-size: 1rem; padding: 0; margin: 0; line-height: 0.7; white-space: nowrap;'>{option['Type']}</div>", unsafe_allow_html=True)
                        with row_cols[1]:
                            st.markdown(f"<div style='font-size: 1rem; padding: 0; margin: 0; line-height: 0.7; white-space: nowrap;'>{option['Name/Combination']}</div>", unsafe_allow_html=True)
                        with row_cols[2]:
                            st.markdown(f"<div style='font-size: 1rem; padding: 0; margin: 0; line-height: 0.7; white-space: nowrap;'>{option['Wattage']}</div>", unsafe_allow_html=True)
                        with row_cols[3]:
                            st.markdown(f"<div style='font-size: 1rem; padding: 0; margin: 0; line-height: 0.7; white-space: nowrap;'>{option['Volt']}</div>", unsafe_allow_html=True)
                        with row_cols[4]:
                            st.markdown(f"<div style='font-size: 1rem; padding: 0; margin: 0; line-height: 0.7; white-space: nowrap;'>{option['Amp']}</div>", unsafe_allow_html=True)
                        with row_cols[5]:
                            st.markdown(f"<div style='font-size: 1rem; padding: 0; margin: 0; line-height: 0.7; white-space: nowrap;'>{option['Price']}</div>", unsafe_allow_html=True)
                        with row_cols[6]:
                            st.markdown(f"<div style='font-size: 1rem; padding: 0; margin: 0; line-height: 0.7; white-space: nowrap;'>{option['Best']}</div>", unsafe_allow_html=True)
                        with row_cols[7]:
                            button_key = f"add_to_table_{idx}_{hash(str(option))}"
                            button_label = "Add"
                            button_type = "primary" if option['Best'] else "secondary"
                            if st.button(button_label, key=button_key, use_container_width=False, type=button_type):
                                try:
                                    # Get display length and unit for the row
                                    display_length, display_unit, _ = _get_calculation()
                                    
                                    # Initialize table_data if not exists
                                    if 'table_data' not in st.session_state:
                                        st.session_state.table_data = []
                                    
                                    # Add to Quotation
                                    row_data = {
                                        "Brand": brand_name or "-",
                                        "Length": f"{display_length} {display_unit}",
                                        "Voltage": option['Volt'],
                                        "LED": led_count,
                                        "Wattage": option['Wattage'],
                                        "Driver": option['Name/Combination'],
                                        "Discount": discount or "-"
                                    }
                                    
                                    st.session_state.table_data.append(row_data)
                                    st.session_state['last_added_item'] = option['Name/Combination']
                                    st.success(f"✅ **{option['Name/Combination']}** added to table!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error adding to table: {e}")
                        
                        if idx < len(all_options_data) - 1:
                            st.markdown("<hr style='margin: 0.05rem 0; border-color: #334155;'>", unsafe_allow_html=True)
                    
                    # Show best option details removed
                else:
                    st.warning(f"⚠️ No drivers found with {cached_voltage}V voltage equal to or above calculated wattage ({cached_wattage}W).")
                    # Still try to find the nearest driver from all drivers with matching voltage (even if below)
                    nearest_driver = None
                    min_diff = float('inf')
                    
                    for driver in all_drivers:
                        driver_watt = driver.get('Watt') or driver.get('watt') or 0
                        driver_volt = driver.get('Volt') or driver.get('volt') or 0
                        
                        # Only consider drivers with matching voltage
                        if driver_volt == cached_voltage and driver_watt >= cached_wattage:
                            watt_diff = driver_watt - cached_wattage
                            if watt_diff < min_diff:
                                min_diff = watt_diff
                                nearest_driver = driver
                    
                    if nearest_driver:
                        nearest_watt = nearest_driver.get('Watt') or nearest_driver.get('watt') or 0
                        nearest_volt = nearest_driver.get('Volt') or nearest_driver.get('volt') or 0
                        nearest_amp = nearest_driver.get('Amp') or nearest_driver.get('amp') or 0
                        nearest_name = nearest_driver.get('Name') or nearest_driver.get('name') or '-'
                        nearest_price = nearest_driver.get('Price') or nearest_driver.get('price')
                        
                        price_text = f" | ₹{nearest_price}" if nearest_price else ""
                        st.info(f"⭐ **Closest Available Driver ({nearest_volt}V):** {nearest_name} | {nearest_watt}W | {nearest_amp}A{price_text} | Difference: +{nearest_watt - cached_wattage:.2f}W")
                    else:
                        st.info(f"ℹ️ No drivers found with {cached_voltage}V voltage in the database.")
            else:
                st.warning("⚠️ No drivers found in the database.")
        except Exception as e:
            st.error(f"❌ Error fetching drivers: {e}")
    elif calculate_clicked:
        st.warning("⚠️ Please enter a valid length (positive integer) and select LED count")

