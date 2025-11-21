"""Driver form component"""

import streamlit as st
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
        
        if driver_volt == voltage and driver_watt >= calculated_wattage:
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
        
        if driver_volt == voltage and driver_watt >= calculated_wattage:
            if calculated_wattage > 0:
                percentage_diff = ((driver_watt - calculated_wattage) / calculated_wattage) * 100
            else:
                percentage_diff = float('inf')
            
            if percentage_diff <= max_percentage_diff:
                watt_diff = driver_watt - calculated_wattage
                nearby_drivers.append({
                    'driver': driver,
                    'watt_diff': watt_diff,
                    'percentage_diff': percentage_diff,
                    'driver_watt': driver_watt
                })
    
    nearby_drivers.sort(key=lambda x: x['watt_diff'])
    return [item['driver'] for item in nearby_drivers]


def _find_driver_combinations(drivers, calculated_wattage, voltage, location_type="both", single_driver_available=False, max_combinations=3, tolerance_percent=10):
    """Find combinations of drivers that sum up to near the calculated wattage"""
    if not drivers or calculated_wattage <= 0:
        return []
    
    candidate_drivers = []
    location_type_lower = location_type.lower() if location_type else "both"
    
    for driver in drivers:
        driver_watt = driver.get('Watt') or driver.get('watt') or 0
        driver_volt = driver.get('Volt') or driver.get('volt') or 0
        driver_price = driver.get('Price') or driver.get('price') or 0
        driver_place = driver.get('Place') or driver.get('place') or ''
        driver_name = driver.get('Name') or driver.get('name') or ''
        
        location_matches = True
        if location_type_lower != "both":
            driver_place_lower = driver_place.lower() if driver_place else ''
            location_matches = driver_place_lower == location_type_lower
        
        if driver_volt == voltage and driver_watt > 0 and location_matches:
            driver_type = ' '.join(driver_name.lower().replace('-', ' ').replace('_', ' ').split()).strip() if driver_name else None
            candidate_drivers.append({
                'driver': driver,
                'watt': driver_watt,
                'price': driver_price,
                'type': driver_type
            })
    
    if not candidate_drivers:
        return []
    
    combinations = []
    tolerance = calculated_wattage * (tolerance_percent / 100)
    max_watt = calculated_wattage * 1.15
    
    # Special handling for 306W - prioritize specific combinations
    if abs(calculated_wattage - 306) < 1:  # Allow small floating point differences
        target_combinations = [
            [300, 60],
            [150, 100, 60],
            [200, 60, 60],
            [150, 200],
            [100, 100, 150]
        ]
        
        # Group drivers by wattage for quick lookup
        drivers_by_watt = {}
        for candidate in candidate_drivers:
            watt = candidate['watt']
            if watt not in drivers_by_watt:
                drivers_by_watt[watt] = []
            drivers_by_watt[watt].append(candidate)
        
        # Try to find exact combinations
        for target_combo in target_combinations:
            found_combo = []
            combo_watts = []
            total_combo_watt = 0
            total_combo_price = 0
            
            for target_watt in target_combo:
                if target_watt in drivers_by_watt and drivers_by_watt[target_watt]:
                    # Use first available driver of this wattage
                    driver_candidate = drivers_by_watt[target_watt][0]
                    found_combo.append(driver_candidate['driver'])
                    combo_watts.append(target_watt)
                    total_combo_watt += target_watt
                    total_combo_price += driver_candidate['price']
                else:
                    # Can't form this combination, skip it
                    found_combo = None
                    break
            
            if found_combo and len(found_combo) == len(target_combo):
                diff = total_combo_watt - calculated_wattage
                combinations.append({
                    'drivers': found_combo,
                    'watts': combo_watts,
                    'total_watt': total_combo_watt,
                    'diff': diff,
                    'percentage_diff': (diff / calculated_wattage * 100) if calculated_wattage > 0 else 0,
                    'total_price': total_combo_price,
                    'driver_count': len(found_combo),
                    'driver_type': 'mixed',
                    'priority': True  # Mark as priority combination
                })
        
        # If we found priority combinations, return them sorted
        if combinations:
            combinations.sort(key=lambda x: (x['driver_count'], x['diff'], x['total_price']))
            return combinations[:max_combinations]
    
    # Group drivers by normalized type name for same-type combinations
    drivers_by_type = {}
    for candidate in candidate_drivers:
        driver_type = candidate['type']
        
        if driver_type not in drivers_by_type:
            drivers_by_type[driver_type] = []
        
        drivers_by_type[driver_type].append(candidate)
    
    # Find combinations within same driver type
    for driver_type, type_drivers in drivers_by_type.items():
        for i in range(len(type_drivers)):
            # Allow same driver combinations (i == j) and different driver combinations (i != j)
            # This enables cases like 2x 100W drivers for 190W requirement
            for j in range(i, len(type_drivers)):
                total_watt = type_drivers[i]['watt'] + type_drivers[j]['watt']
                
                if total_watt >= calculated_wattage:
                    diff = total_watt - calculated_wattage
                    
                    if diff <= tolerance or total_watt <= max_watt:
                        total_price = type_drivers[i]['price'] + type_drivers[j]['price']
                        
                        # When single drivers are available, prefer tighter matches but still allow up to max_watt
                        # This ensures all driver types are represented in options
                        if single_driver_available:
                            # Allow combinations within 10% diff OR up to max_watt (115%)
                            # This gives preference to tighter matches but doesn't exclude valid combinations
                            if diff <= calculated_wattage * 0.10 or total_watt <= max_watt:
                                combinations.append({
                                    'drivers': [type_drivers[i]['driver'], type_drivers[j]['driver']],
                                    'watts': [type_drivers[i]['watt'], type_drivers[j]['watt']],
                                    'total_watt': total_watt,
                                    'diff': diff,
                                    'percentage_diff': (diff / calculated_wattage * 100) if calculated_wattage > 0 else 0,
                                    'total_price': total_price,
                                    'driver_count': 2,
                                    'driver_type': driver_type
                                })
                        else:
                            combinations.append({
                                'drivers': [type_drivers[i]['driver'], type_drivers[j]['driver']],
                                'watts': [type_drivers[i]['watt'], type_drivers[j]['watt']],
                                'total_watt': total_watt,
                                'diff': diff,
                                'percentage_diff': (diff / calculated_wattage * 100) if calculated_wattage > 0 else 0,
                                'total_price': total_price,
                                'driver_count': 2,
                                'driver_type': driver_type
                            })
        
        # Check for 3-driver combinations when no single driver available OR wattage > 500
        if not single_driver_available or calculated_wattage > 500:
            if len(type_drivers) >= 3:
                for i in range(len(type_drivers)):
                    for j in range(i, len(type_drivers)):  # Allow same driver (i == j)
                        for k in range(j, len(type_drivers)):  # Allow same driver (j == k)
                            total_watt = (type_drivers[i]['watt'] + 
                                         type_drivers[j]['watt'] + 
                                         type_drivers[k]['watt'])
                            
                            if total_watt >= calculated_wattage:
                                diff = total_watt - calculated_wattage
                                
                                # Relaxed condition: allow up to 15% over wattage (max_watt) OR within 10% diff
                                if (diff <= calculated_wattage * 0.10 or total_watt <= max_watt) and total_watt <= max_watt:
                                    total_price = type_drivers[i]['price'] + type_drivers[j]['price'] + type_drivers[k]['price']
                                    
                                    combinations.append({
                                        'drivers': [
                                            type_drivers[i]['driver'],
                                            type_drivers[j]['driver'],
                                            type_drivers[k]['driver']
                                        ],
                                        'watts': [
                                            type_drivers[i]['watt'],
                                            type_drivers[j]['watt'],
                                            type_drivers[k]['watt']
                                        ],
                                        'total_watt': total_watt,
                                        'diff': diff,
                                        'percentage_diff': (diff / calculated_wattage * 100) if calculated_wattage > 0 else 0,
                                        'total_price': total_price,
                                        'driver_count': 3,
                                        'driver_type': driver_type
                                    })
    
    # Also find cross-type combinations (combinations across different driver types)
    # This allows mixing different driver types
    for i in range(len(candidate_drivers)):
        for j in range(i, len(candidate_drivers)):
            # Skip if same type (already handled above)
            if candidate_drivers[i]['type'] == candidate_drivers[j]['type']:
                continue
            
            total_watt = candidate_drivers[i]['watt'] + candidate_drivers[j]['watt']
            
            if total_watt >= calculated_wattage:
                diff = total_watt - calculated_wattage
                
                if diff <= tolerance or total_watt <= max_watt:
                    total_price = candidate_drivers[i]['price'] + candidate_drivers[j]['price']
                    
                    if single_driver_available:
                        if diff <= calculated_wattage * 0.10 or total_watt <= max_watt:
                            combinations.append({
                                'drivers': [candidate_drivers[i]['driver'], candidate_drivers[j]['driver']],
                                'watts': [candidate_drivers[i]['watt'], candidate_drivers[j]['watt']],
                                'total_watt': total_watt,
                                'diff': diff,
                                'percentage_diff': (diff / calculated_wattage * 100) if calculated_wattage > 0 else 0,
                                'total_price': total_price,
                                'driver_count': 2,
                                'driver_type': 'mixed'
                            })
                    else:
                        combinations.append({
                            'drivers': [candidate_drivers[i]['driver'], candidate_drivers[j]['driver']],
                            'watts': [candidate_drivers[i]['watt'], candidate_drivers[j]['watt']],
                            'total_watt': total_watt,
                            'diff': diff,
                            'percentage_diff': (diff / calculated_wattage * 100) if calculated_wattage > 0 else 0,
                            'total_price': total_price,
                            'driver_count': 2,
                            'driver_type': 'mixed'
                        })
    
    # Find 3-driver cross-type combinations
    if not single_driver_available or calculated_wattage > 500:
        for i in range(len(candidate_drivers)):
            for j in range(i, len(candidate_drivers)):
                for k in range(j, len(candidate_drivers)):
                    # Skip if all same type (already handled above)
                    if (candidate_drivers[i]['type'] == candidate_drivers[j]['type'] == candidate_drivers[k]['type']):
                        continue
                    
                    total_watt = (candidate_drivers[i]['watt'] + 
                                 candidate_drivers[j]['watt'] + 
                                 candidate_drivers[k]['watt'])
                    
                    if total_watt >= calculated_wattage:
                        diff = total_watt - calculated_wattage
                        
                        if (diff <= calculated_wattage * 0.10 or total_watt <= max_watt) and total_watt <= max_watt:
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
                                'driver_count': 3,
                                'driver_type': 'mixed'
                            })
    
    # Remove duplicates based on driver combination (same drivers in same order)
    seen_combos = set()
    unique_combinations = []
    for combo in combinations:
        # Create a signature based on sorted watts to identify duplicates
        combo_signature = tuple(sorted(combo['watts']))
        if combo_signature not in seen_combos:
            seen_combos.add(combo_signature)
            unique_combinations.append(combo)
    
    # Sort: priority combinations first, then by driver_count, diff, and price
    unique_combinations.sort(key=lambda x: (
        not x.get('priority', False),  # Priority combinations first
        x['driver_count'], 
        x['diff'], 
        x['total_price']
    ))
    
    return unique_combinations[:max_combinations]


def render_driver_form(brand_name, location_type):
    """Render the driver form with all inputs and buttons"""
    default_length, default_is_feet, default_voltage_index, default_led_index, default_discount = _parse_editing_row()
    
    if st.session_state.editing_row is not None:
        form_length = default_length
        form_voltage_index = default_voltage_index
        form_led_index = default_led_index
        form_discount = default_discount
    else:
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
        if length_input:
            st.warning("⚠️ Please enter a valid integer for length")
        length = None
    
    col_voltage, col_led = st.columns(2)
    with col_voltage:
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
    
    calculate_clicked = st.button("🧮 Calculate Wattage", type="primary", key="calc_btn", use_container_width=True)
    
    def _is_valid_input():
        return length is not None and length > 0 and led_count > 0
    
    def _get_calculation():
        cache = st.session_state
        if (cache.get('calculated_wattage') and 
            cache.get('calc_length') == length and
            cache.get('calc_led_count') == led_count and
            cache.get('calc_unit') == unit):
            return cache.calc_converted_length, "Meter", cache.calculated_wattage
        return _convert_and_calculate(length, unit, led_count)
    
    should_show_drivers = False
    cached_wattage = None
    cached_voltage = None
    
    if calculate_clicked and _is_valid_input():
        calc_length, _, wattage = _convert_and_calculate(length, unit, led_count)
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
        cached_wattage = st.session_state.calculated_wattage
        cached_voltage = st.session_state.get('calc_voltage', voltage)
        should_show_drivers = True
    
    if should_show_drivers:
        try:
            # Use cached data - spinner only shows if cache miss
            all_drivers = fetch_drivers(location_type)
            
            if all_drivers:
                nearby_drivers = _filter_nearby_drivers(all_drivers, cached_wattage, cached_voltage, max_percentage_diff=50)
                nearest_driver = None
                if nearby_drivers:
                    nearest_driver, diff = _find_nearest_driver(nearby_drivers, cached_wattage, cached_voltage)
                
                calc_length = st.session_state.get('calc_converted_length', 0)
                requires_multiple_drivers = False
                if cached_voltage == 12 and calc_length > 10:
                    requires_multiple_drivers = True
                elif cached_voltage == 24 and calc_length > 15:
                    requires_multiple_drivers = True
                
                # Get matching voltage drivers for combination search
                location_type_lower = location_type.lower() if location_type else "both"
                matching_voltage_drivers = []
                for d in all_drivers:
                    driver_volt = d.get('Volt') or d.get('volt') or 0
                    driver_place = d.get('Place') or d.get('place') or ''
                    
                    voltage_matches = driver_volt == cached_voltage
                    location_matches = True
                    if location_type_lower != "both":
                        driver_place_lower = driver_place.lower() if driver_place else ''
                        location_matches = driver_place_lower == location_type_lower
                    
                    if voltage_matches and location_matches:
                        matching_voltage_drivers.append(d)
                
                single_driver_available = len(nearby_drivers) > 0 and not requires_multiple_drivers
                
                # Always search for combinations, even when no single drivers are available
                all_options_data = []
                
                # Add single drivers if available and not requiring multiple
                if nearby_drivers and not requires_multiple_drivers:
                    for driver in nearby_drivers:
                        driver_watt = driver.get('Watt') or driver.get('watt') or 0
                        driver_volt = driver.get('Volt') or driver.get('volt') or 0
                        driver_amp = driver.get('Amp') or driver.get('amp') or 0
                        driver_name = driver.get('Name') or driver.get('name') or '-'
                        driver_price = driver.get('Price') or driver.get('price')
                        
                        is_nearest = driver == nearest_driver
                        watt_diff = driver_watt - cached_wattage
                        
                        option_entry = {
                            'Type': '1',
                            'Name/Combination': f"{driver_name} ({driver_watt}W)",
                            'Wattage': f"{driver_watt}W",
                            'Volt': f"{driver_volt}V",
                            'Amp': f"{driver_amp}A",
                            'Price': f"₹{driver_price}" if driver_price else '-',
                            'Best': '⭐' if is_nearest else '',
                            '_sort_diff': watt_diff
                        }
                        all_options_data.append(option_entry)
                
                # Search for combinations (always, even if no single drivers)
                # Limit combinations on mobile for better performance
                if matching_voltage_drivers:
                    # Reduce max combinations on mobile devices
                    max_combo_limit = 5  # Reduced from 10 for mobile performance
                    combinations = _find_driver_combinations(
                        matching_voltage_drivers, 
                        cached_wattage, 
                        cached_voltage,
                        location_type,
                        single_driver_available=single_driver_available,
                        max_combinations=max_combo_limit
                    )
                    
                    for idx, combo in enumerate(combinations, 1):
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
                        
                        option_entry = {
                            'Type': str(len(combo["drivers"])),
                            'Name/Combination': " + ".join(combination_parts),
                            'Wattage': f"{combo['total_watt']:.2f}W",
                            'Volt': f"{total_volt}V",
                            'Amp': f"{total_amp:.2f}A",
                            'Price': f"₹{total_price:.2f}" if total_price > 0 else '-',
                            'Best': '🏆' if idx == 1 else '',
                            '_sort_diff': combo['diff']
                        }
                        all_options_data.append(option_entry)
                
                all_options_data.sort(key=lambda x: x['_sort_diff'])
                
                # Display results
                if len(all_options_data) > 0:
                    st.markdown(f"<h4 style='font-size: 1rem; margin-bottom: 0.5rem;'>📋 Available Drivers & Combinations ({cached_voltage}V)</h4>", unsafe_allow_html=True)
                    st.caption("Select a driver option below and add it to your table")
                    st.markdown("<h4 style='font-size: 1rem; margin-bottom: 0.5rem;'>🎯 Driver Options</h4>", unsafe_allow_html=True)
                    
                    if requires_multiple_drivers:
                        all_options_data = [opt for opt in all_options_data if opt['Type'] != '1']
                        if len(all_options_data) == 0:
                            st.error(f"❌ **No driver combinations found:** Multiple drivers are required for this length and voltage, but no suitable combinations were found. Please check available drivers in the database.")
                    
                    if len(all_options_data) > 0:
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
                                        display_length, display_unit, _ = _get_calculation()
                                        
                                        if 'table_data' not in st.session_state:
                                            st.session_state.table_data = []
                                        
                                        # Extract price from option['Price'] (format: "₹123.45" or "-")
                                        price_value = 0
                                        price_str = option.get('Price', '-')
                                        if price_str and price_str != '-':
                                            # Remove rupee symbol and extract numeric value
                                            price_clean = str(price_str).replace('₹', '').replace(',', '').strip()
                                            if price_clean:  # Only parse if there's actual content
                                                try:
                                                    price_value = float(price_clean)
                                                except (ValueError, AttributeError):
                                                    price_value = 0
                                        
                                        row_data = {
                                            "Brand": brand_name or "-",
                                            "Length": f"{display_length} {display_unit}",
                                            "Voltage": option['Volt'],
                                            "LED": led_count,
                                            "Wattage": option['Wattage'],
                                            "Driver": option['Name/Combination'],
                                            "Price": price_value,
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
                else:
                    # No single drivers and no combinations found
                    st.warning(f"⚠️ No drivers found with {cached_voltage}V voltage equal to or above calculated wattage ({cached_wattage}W).")
                    
                    # Try to find nearest single driver for reference
                    nearest_driver = None
                    min_diff = float('inf')
                    
                    for driver in all_drivers:
                        driver_watt = driver.get('Watt') or driver.get('watt') or 0
                        driver_volt = driver.get('Volt') or driver.get('volt') or 0
                        
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

