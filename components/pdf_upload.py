"""PDF upload component for inserting driver data"""

import streamlit as st
import pdfplumber
import re
import pandas as pd
from supabase_client import insert_drivers_batch, authenticate_user, fetch_drivers, fetch_brands_with_ids


def _parse_product_name(product_name: str):
    """
    Parse product name to extract simplified Name, Volt, Watt, and Amp.
    Example: "SMPS - Slim - 12V - 36W - 3Amp" -> "smps slim", 12, 36, 3.0
    Handles fragmented text like "8.5A" + "mp" or "3A" without "mp"
    """
    if not product_name:
        return None
    
    # Clean up the product name first - handle fragmented amperage
    # Fix patterns like "8. mp" -> "8.5Amp" or "3A" -> "3Amp"
    product_name = re.sub(r'(\d+\.?\d*)\s*A\s*m\s*p', r'\1Amp', product_name, flags=re.IGNORECASE)
    product_name = re.sub(r'(\d+\.?\d*)\s*A\s*m\s*$', r'\1Amp', product_name, flags=re.IGNORECASE)
    # Handle cases where "A" is separated from number (e.g., "8.5 A" or "3 A")
    product_name = re.sub(r'(\d+\.?\d*)\s+A\s*(?:mp)?', r'\1Amp', product_name, flags=re.IGNORECASE)
    # Handle cases where just "A" is present (e.g., "3A" or "8.5A")
    product_name = re.sub(r'(\d+\.?\d*)\s*A\s*(?!\w)', r'\1Amp', product_name, flags=re.IGNORECASE)
    
    # Extract simplified name
    # Remove color specifications like "(Black)", "(White)", etc.
    product_name_clean = re.sub(r'\s*\([^)]+\)\s*', ' ', product_name)
    
    # Remove duplicate product names that might appear at the end
    # Pattern: "Dimmable 4 in 1 ... Dimmable 4 in 1" -> "Dimmable 4 in 1"
    # Pattern: "Waterproof SMPS ... Waterproof SMPS" -> "Waterproof SMPS"
    words = product_name_clean.split()
    if len(words) >= 4:
        # Check if last words duplicate the first words (check various lengths)
        # Start from longer matches and work down
        for check_len in range(min(5, len(words) // 2), 1, -1):
            if len(words) >= check_len * 2:
                first_words = ' '.join(words[:check_len]).lower()
                last_words = ' '.join(words[-check_len:]).lower()
                if first_words == last_words:
                    product_name_clean = ' '.join(words[:-check_len])
                    break
    
    # Try splitting by " - " first (for formatted names)
    parts = product_name_clean.split(' - ')
    
    # Extract name - take parts before voltage specification
    simplified_name = None
    
    # Find where voltage starts (first part containing "V")
    volt_start_idx = None
    for idx, part in enumerate(parts):
        if re.search(r'\d+V', part):
            volt_start_idx = idx
            break
    
    if volt_start_idx is not None and volt_start_idx > 0:
        # Take all parts before voltage
        name_parts = parts[:volt_start_idx]
        simplified_name = ' '.join(name_parts).strip()
    elif len(parts) == 1:
        # No " - " separator, extract name by removing voltage/wattage/amperage patterns
        # Examples:
        # "Waterproof SMPS 24V 12.5Amp" -> "Waterproof SMPS"
        # "Waterproof SMPS 12V 8.3Amp" -> "Waterproof SMPS"
        # "Waterproof SMPS 12V 25Amp" -> "Waterproof SMPS"
        # "Waterproof SMPS" -> "Waterproof SMPS" (no changes needed)
        # "imma ble 4 in 1" -> will be fixed by fragmentation fixes below
        text = parts[0]
        
        # Split into words and filter out technical specifications
        words = text.split()
        filtered_words = []
        
        for word in words:
            word_clean = word.strip()
            if not word_clean:
                continue
                
            # Check if word matches voltage pattern (e.g., "24V", "12V", "48V")
            if re.match(r'^\d+V$', word_clean, re.IGNORECASE):
                continue
            # Check if word matches wattage pattern (e.g., "100W", "50W")
            if re.match(r'^\d+W$', word_clean, re.IGNORECASE):
                continue
            # Check if word matches amperage pattern (e.g., "12.5Amp", "8.3Amp", "25Amp", "8.3A", "25A")
            # Match: digits (optional decimal) followed by A or Amp
            if re.match(r'^\d+\.?\d*A(?:mp)?$', word_clean, re.IGNORECASE):
                continue
            # Keep the word if it doesn't match any technical pattern
            filtered_words.append(word_clean)
        
        simplified_name = ' '.join(filtered_words).strip()
        
        # If filtering resulted in empty name, use original text (shouldn't happen, but safety check)
        if not simplified_name:
            simplified_name = text.strip()
    elif len(parts) >= 2:
        # Fallback: take first two parts
        simplified_name = f"{parts[0]} {parts[1]}".strip()
    else:
        # Fallback: use first part only
        simplified_name = parts[0].strip() if parts else product_name_clean.strip()
    
    # Fix fragmented names (e.g., "imma ble" -> "Dimmable")
    # Common fragmentation patterns
    fragmentation_fixes = {
        r'\bimma\s+ble\b': 'Dimmable',
        r'\bdimm\s+able\b': 'Dimmable',
        r'\bdimm\s+ab\s*le\b': 'Dimmable',
        r'\bwa\s+ter\s*proof\b': 'Waterproof',
        r'\bwa\s+ter\s*pr\s*oof\b': 'Waterproof',
        r'\bdi\s+mmab\s*le\b': 'Dimmable',
        r'\bdi\s+mm\s*able\b': 'Dimmable',
    }
    
    for pattern, replacement in fragmentation_fixes.items():
        simplified_name = re.sub(pattern, replacement, simplified_name, flags=re.IGNORECASE)
    
    # Remove duplicate fragments at the end (e.g., "DALI Dimmable DALI SMP" -> "DALI Dimmable")
    # Check if last words are fragments/duplicates of the beginning
    words = simplified_name.split()
    if len(words) >= 3:
        # Check if ending is "DALI SMP" or "DALI" and remove it
        if len(words) >= 2 and words[-2:][0].upper() == 'DALI' and words[-1].upper() in ['SMP', 'SMPS']:
            simplified_name = ' '.join(words[:-2]).strip()
        elif len(words) >= 1 and words[-1].upper() == 'DALI' and len(words) > 1:
            # Only remove if "DALI" appears at the end and there's already "DALI" earlier
            if 'DALI' in [w.upper() for w in words[:-1]]:
                simplified_name = ' '.join(words[:-1]).strip()
    
    # Final cleanup: remove any remaining technical specifications that might have been missed
    # Split and filter again to catch any patterns that weren't removed earlier
    final_words = simplified_name.split()
    final_filtered = []
    for word in final_words:
        word_clean = word.strip()
        if not word_clean:
            continue
        # Skip voltage, wattage, and amperage patterns
        if (re.match(r'^\d+V$', word_clean, re.IGNORECASE) or
            re.match(r'^\d+W$', word_clean, re.IGNORECASE) or
            re.match(r'^\d+\.?\d*A(?:mp)?$', word_clean, re.IGNORECASE)):
            continue
        final_filtered.append(word_clean)
    
    simplified_name = ' '.join(final_filtered).strip()
    
    # Clean up and normalize (remove extra spaces, but keep capitalization)
    simplified_name = re.sub(r'\s+', ' ', simplified_name).strip()
    
    # Extract voltage (e.g., 12V, 24V, 48V)
    volt_match = re.search(r'(\d+)V', product_name)
    volt = int(volt_match.group(1)) if volt_match else None
    
    # Extract wattage (e.g., 36W, 60W) - make it optional
    watt_match = re.search(r'(\d+)W', product_name)
    watt = int(watt_match.group(1)) if watt_match else None
    
    # Extract amperage - more flexible patterns
    # Try full "Amp" first
    amp_match = re.search(r'(\d+\.?\d*)\s*Amp', product_name, re.IGNORECASE)
    if not amp_match:
        # Try just "A" (e.g., "3A", "8.5A", "12.5A")
        amp_match = re.search(r'(\d+\.?\d*)\s*A\s*(?!\w)', product_name, re.IGNORECASE)
    
    amp = float(amp_match.group(1)) if amp_match else None
    
    # Volt is required, but watt and amp can be optional for some products
    if volt is None:
        return None
    
    # If amp is missing, set it to 0 (don't calculate from watt/volt)
    if amp is None:
        amp = 0.0
    
    # If watt is missing, we can calculate it from volt and amp: W = V * A
    # But only if amp is greater than 0
    if watt is None and volt is not None and amp is not None and amp > 0:
        watt = int(volt * amp)
    
    # If both watt and amp are missing (amp is 0), we can't proceed
    if watt is None and amp == 0:
        return None
    
    return {
        'Name': simplified_name,
        'Volt': volt,
        'Watt': watt,
        'Amp': amp
    }


def _extract_table_from_pdf(pdf_file):
    """Extract table data from PDF file"""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            all_tables = []
            for page_num, page in enumerate(pdf.pages):
                # Try multiple extraction strategies
                # First try with explicit line detection
                tables = page.extract_tables(
                    table_settings={
                        "vertical_strategy": "lines_strict",
                        "horizontal_strategy": "lines_strict",
                        "snap_tolerance": 3,
                        "join_tolerance": 3,
                    }
                )
                if tables:
                    all_tables.extend(tables)
                else:
                    # Fallback: try with text-based strategy
                    tables = page.extract_tables(
                        table_settings={
                            "vertical_strategy": "text",
                            "horizontal_strategy": "text",
                        }
                    )
                    if tables:
                        all_tables.extend(tables)
                    else:
                        # Final fallback: default settings
                        tables = page.extract_tables()
                        if tables:
                            all_tables.extend(tables)
            return all_tables
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None


def _reconstruct_product_name_from_row(row):
    """Reconstruct product name from fragmented cells in a row"""
    if not row:
        return None, None
    
    # Combine all non-empty cells to reconstruct the product name
    combined_parts = []
    price = None
    last_part = None
    
    for cell in row:
        if cell:
            cell_str = str(cell).strip()
            if not cell_str:
                continue
            
            # Check if it's a price (numeric value, usually at the end)
            if re.match(r'^\d+\.?\d*$', cell_str):
                try:
                    price_val = float(cell_str)
                    # Price is usually larger (like 460, 600, etc.) and appears later in row
                    if price_val > 10:  # Reasonable price threshold
                        price = price_val
                        continue
                except:
                    pass
            
            # Handle single characters that might be fragments (like "m", "p" from "Amp")
            if len(cell_str) == 1:
                # If previous part ends with a number or "A", this might be part of "Amp"
                if last_part and (re.search(r'\d+\.?\d*\s*$', last_part) or last_part.endswith('A')):
                    # Combine with previous part
                    if combined_parts:
                        combined_parts[-1] = combined_parts[-1] + cell_str
                    else:
                        combined_parts.append(cell_str)
                else:
                    # Skip isolated single characters
                    continue
            else:
                # Check if this starts with a fragment that should be combined with previous
                # (e.g., previous was "8.5A" and this is "mp")
                if last_part and len(cell_str) <= 3 and re.match(r'^[a-z]+$', cell_str, re.IGNORECASE):
                    # Check if previous part ends with a number or "A"
                    if re.search(r'\d+\.?\d*\s*A?\s*$', last_part, re.IGNORECASE):
                        combined_parts[-1] = combined_parts[-1] + cell_str
                        last_part = combined_parts[-1]
                        continue
                
                combined_parts.append(cell_str)
                last_part = cell_str
    
    if not combined_parts:
        return None, None
    
    # Join parts and clean up
    product_name = ' '.join(combined_parts)
    # Clean up common fragmentation patterns
    product_name = re.sub(r'\s+', ' ', product_name)  # Multiple spaces
    product_name = re.sub(r'\s*-\s*', ' - ', product_name)  # Normalize dashes
    product_name = re.sub(r'\s*([0-9]+V)\s*', r' \1 ', product_name)  # Normalize voltage
    product_name = re.sub(r'\s*([0-9]+W)\s*', r' \1 ', product_name)  # Normalize wattage
    # Fix fragmented amperage patterns
    product_name = re.sub(r'(\d+\.?\d*)\s*A\s*m\s*p', r'\1Amp', product_name, flags=re.IGNORECASE)
    product_name = re.sub(r'(\d+\.?\d*)\s*A\s*(?!\w)', r'\1Amp', product_name, flags=re.IGNORECASE)
    product_name = re.sub(r'(\d+\.?\d*)\s+A\s*(?:mp)?', r'\1Amp', product_name, flags=re.IGNORECASE)
    product_name = product_name.strip()
    
    return product_name, price


def _parse_pdf_tables(tables, show_debug=False, brand_id=None):
    """Parse extracted tables and extract driver data"""
    drivers = []
    
    if not tables:
        return drivers
    
    for table_idx, table in enumerate(tables):
        if not table:
            continue
        
        if len(table) < 2:  # Need at least header + 1 data row
            if show_debug:
                st.write(f"Table {table_idx}: Skipped - too few rows ({len(table)})")
            continue
        
        # Find column indices - check all rows in case header is not first row
        header_row_idx = 0
        product_col_idx = None
        price_col_idx = None
        
        # Try to find header row (might not be first row)
        # Check more rows and be more flexible with column name matching
        for row_idx, row in enumerate(table[:10]):  # Check first 10 rows for header
            if not row:
                continue
            for idx, col in enumerate(row):
                if col:
                    col_str = str(col).upper().strip()
                    # More flexible matching for PRODUCT column
                    if product_col_idx is None and ('PRODUCT' in col_str or 'NAME' in col_str or 'ITEM' in col_str):
                        product_col_idx = idx
                        header_row_idx = row_idx
                        if show_debug:
                            st.write(f"Table {table_idx}: Found PRODUCT column at index {idx} in row {row_idx}: '{col_str}'")
                    # More flexible matching for PRICE column
                    if price_col_idx is None and ('PRICE' in col_str or 'COST' in col_str):
                        price_col_idx = idx
                        header_row_idx = row_idx
                        if show_debug:
                            st.write(f"Table {table_idx}: Found PRICE column at index {idx} in row {row_idx}: '{col_str}'")
        
        # If no header found, try to reconstruct product names from entire rows
        # This handles cases where product names are split across multiple columns
        if product_col_idx is None:
            if show_debug:
                st.write(f"Table {table_idx}: PRODUCT column not found in headers, trying to reconstruct from row data...")
            # Process rows directly without column index
            product_col_idx = -1  # Special flag to use row reconstruction
        
        # Extract data rows (skip header row and any rows before it)
        rows_processed = 0
        rows_skipped = 0
        
        # Determine start row (skip header if found)
        start_row = header_row_idx + 1 if header_row_idx >= 0 else 0
        
        for row_idx, row in enumerate(table[start_row:], start=start_row):
            if not row:
                rows_skipped += 1
                continue
            
            # If product_col_idx is -1, reconstruct from entire row
            if product_col_idx == -1:
                product_name, extracted_price = _reconstruct_product_name_from_row(row)
                if not product_name:
                    rows_skipped += 1
                    continue
                
                # Skip if it looks like a header
                if product_name.upper() in ['PRODUCT', 'NAME', '']:
                    rows_skipped += 1
                    continue
                
                price = extracted_price
            else:
                # Use specific column
                # Ensure row has enough columns
                while len(row) <= product_col_idx:
                    row.append(None)
                
                product_cell = row[product_col_idx]
                
                # Skip empty cells, header-like cells, and non-string values
                if not product_cell:
                    rows_skipped += 1
                    continue
                
                product_name = str(product_cell).strip()
                
                # Skip if it looks like a header or empty
                if not product_name or product_name.upper() in ['PRODUCT', 'NAME', '']:
                    rows_skipped += 1
                    continue
                
                # Extract price if available
                price = None
                if price_col_idx is not None and len(row) > price_col_idx and row[price_col_idx]:
                    try:
                        price_str = str(row[price_col_idx]).strip()
                        # Remove any non-numeric characters except decimal point
                        price_str = re.sub(r'[^\d.]', '', price_str)
                        if price_str:
                            price = float(price_str)
                    except (ValueError, TypeError):
                        price = None
            
            # Try to parse the product name
            parsed_data = _parse_product_name(product_name)
            if not parsed_data:
                if show_debug:
                    st.write(f"Row {row_idx}: Skipped - Could not parse: '{product_name}'")
                    # Show what was found
                    volt_match = re.search(r'(\d+)V', product_name)
                    watt_match = re.search(r'(\d+)W', product_name)
                    amp_match = re.search(r'(\d+\.?\d*)Amp', product_name)
                    st.write(f"  Volt found: {volt_match.group(1) if volt_match else 'No'}, "
                           f"Watt found: {watt_match.group(1) if watt_match else 'No'}, "
                           f"Amp found: {amp_match.group(1) if amp_match else 'No'}")
                rows_skipped += 1
                continue
            
            # Add price and brand_id
            parsed_data['Price'] = price
            parsed_data['Bid'] = brand_id if brand_id else 1  # Use selected brand or default to 1
            
            drivers.append(parsed_data)
            rows_processed += 1
        
        if show_debug:
            st.write(f"Table {table_idx}: Processed {rows_processed} rows, Skipped {rows_skipped} rows")
    
    return drivers


def render_pdf_upload():
    """Render PDF upload form and handle data insertion"""
    st.subheader("📄 Upload Drivers")
    
    # Authentication section
    import os
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    is_authenticated = st.session_state.get('supabase_user') is not None
    
    if not service_role_key and not is_authenticated:
        st.info("🔐 **Authentication Required:** You need to authenticate to insert data into the database.")
        with st.expander("🔑 Sign In", expanded=True):
            email = st.text_input("Email", key="auth_email")
            password = st.text_input("Password", type="password", key="auth_password")
            
            col_auth1, col_auth2 = st.columns([1, 1])
            with col_auth1:
                if st.button("Sign In", type="primary", use_container_width=True):
                    if email and password:
                        success, message = authenticate_user(email, password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.warning("Please enter both email and password")
        
        st.markdown("---")
        return
    
    # Check if drivers exist in database
    try:
        existing_drivers = fetch_drivers()
        has_drivers = len(existing_drivers) > 0
    except Exception as e:
        st.warning(f"Could not fetch drivers: {e}")
        existing_drivers = []
        has_drivers = False
    
    # Fetch brands for dropdown
    try:
        brands_with_ids = fetch_brands_with_ids()
        brand_dict = {brand['name']: brand['id'] for brand in brands_with_ids}
        brand_names = [brand['name'] for brand in brands_with_ids]
        # Create a mapping of Bid to Brand name (for display purposes)
        bid_to_brand = {brand['id']: brand['name'] for brand in brands_with_ids}
    except Exception as e:
        st.warning(f"Could not fetch brands: {e}")
        brands_with_ids = []
        brand_dict = {}
        brand_names = []
        bid_to_brand = {}
    
    # Show existing drivers if available
    if has_drivers:
        with st.expander("### 📊 Existing Drivers in Database", expanded=False):
            # Replace Bid with Brand name in the display and remove id column
            display_drivers = []
            for driver in existing_drivers:
                display_driver = driver.copy()
                # Remove id column
                display_driver.pop('id', None)
                display_driver.pop('Id', None)
                display_driver.pop('ID', None)
                
                bid = driver.get('Bid') or driver.get('bid')
                if bid and bid in bid_to_brand:
                    display_driver['Brand'] = bid_to_brand[bid]
                    # Remove Bid from display
                    display_driver.pop('Bid', None)
                    display_driver.pop('bid', None)
                else:
                    display_driver['Brand'] = f"Brand ID: {bid}" if bid else "No Brand"
                    display_driver.pop('Bid', None)
                    display_driver.pop('bid', None)
                display_drivers.append(display_driver)
            
            drivers_df = pd.DataFrame(display_drivers)
            st.dataframe(drivers_df, use_container_width=True, hide_index=True)
        st.markdown("---")
    
    # Manual driver insertion form
    st.markdown("### ➕ Add Driver Manually")
    st.markdown("Fill in the driver details below to add a new driver to the database.")
    
    with st.form("manual_driver_form"):
        if brand_names:
            selected_brand = st.selectbox("Brand", brand_names, key="manual_brand")
            selected_brand_id = brand_dict.get(selected_brand)
        else:
            st.warning("⚠️ No brands found in database. Please add brands first.")
            selected_brand_id = None
        
        col1, col2 = st.columns(2)
        with col1:
            driver_name = st.text_input("Driver Name", placeholder="e.g., SMPS - Slim", key="manual_name")
            driver_volt = st.number_input("Voltage (V)", min_value=0, value=12, step=1, key="manual_volt")
        with col2:
            driver_watt = st.number_input("Wattage (W)", min_value=0, value=0, step=1, key="manual_watt")
            driver_amp = st.number_input("Amperage (A)", min_value=0.0, value=0.0, step=0.1, format="%.1f", key="manual_amp")
        
        driver_price = st.number_input("Price (₹) - Optional", min_value=0.0, value=0.0, step=1.0, format="%.2f", key="manual_price")
        
        col_submit, col_clear = st.columns([1, 1])
        with col_submit:
            submit_manual = st.form_submit_button("Insert Driver", type="primary", use_container_width=True)
        with col_clear:
            clear_manual = st.form_submit_button("Clear Form", use_container_width=True)
        
        if submit_manual:
            if driver_name and driver_name.strip() and driver_volt > 0:
                if not selected_brand_id:
                    st.warning("⚠️ Please select a brand")
                elif driver_watt > 0 or driver_amp > 0:
                    try:
                        driver_data = {
                            'Name': driver_name.strip(),
                            'Volt': int(driver_volt),
                            'Watt': int(driver_watt) if driver_watt > 0 else None,
                            'Amp': float(driver_amp) if driver_amp > 0 else None,
                            'Bid': selected_brand_id
                        }
                        if driver_price > 0:
                            driver_data['Price'] = float(driver_price)
                        
                        # Remove None values (but keep Bid)
                        driver_data = {k: v for k, v in driver_data.items() if v is not None or k == 'Bid'}
                        
                        with st.spinner("Inserting driver into database..."):
                            result = insert_drivers_batch([driver_data])
                            st.success(f"✅ Successfully inserted driver: {driver_name}")
                            st.balloons()
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error inserting driver: {e}")
                else:
                    st.warning("⚠️ Please enter either Wattage or Amperage (at least one is required)")
            else:
                st.warning("⚠️ Please enter Driver Name and Voltage (both are required)")
        
        if clear_manual:
            # Clear form by rerunning (form will reset to default values)
            st.rerun()
    
    st.markdown("---")
    
    # PDF Upload section
    st.markdown("### 📄 Upload Drivers from PDF")
    st.markdown("Upload a PDF file containing driver product information. The system will extract product details and insert them into the drivers table.")
    
    # Brand selection for PDF upload
    if brand_names:
        pdf_brand = st.selectbox("Select Brand for PDF Upload", brand_names, key="pdf_brand")
        pdf_brand_id = brand_dict.get(pdf_brand)
    else:
        st.warning("⚠️ No brands found in database. Please add brands first.")
        pdf_brand_id = None
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF file with a table containing PRODUCT, GROUP, and PRICE columns"
    )
    
    if uploaded_file is not None:
        # Show file info
        st.info(f"📎 File uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Extract tables from PDF
        with st.spinner("Extracting data from PDF..."):
            tables = _extract_table_from_pdf(uploaded_file)
        
        if tables is None:
            st.error("Failed to extract tables from PDF.")
            return
        
        # Show debug info - always expanded if no data found
        show_debug_expanded = len(tables) == 0 or (len(tables) > 0 and len(tables[0]) == 0)
        with st.expander("🔍 Debug: Raw Table Data", expanded=show_debug_expanded):
            st.write(f"Found {len(tables)} table(s) in PDF")
            if len(tables) == 0:
                st.warning("No tables found in PDF. The PDF might not contain extractable tables.")
            for idx, table in enumerate(tables):
                st.write(f"**Table {idx + 1}** ({len(table)} rows):")
                if table:
                    # Show all rows for debugging
                    for row_idx, row in enumerate(table):
                        st.write(f"Row {row_idx}: {row}")
                    # Also show column analysis
                    if len(table) > 0:
                        st.write("**Column Analysis:**")
                        for col_idx in range(max(len(row) for row in table if row)):
                            col_values = [str(row[col_idx]).strip() if row and len(row) > col_idx and row[col_idx] else "" 
                                         for row in table[:10]]  # First 10 rows
                            non_empty = [v for v in col_values if v]
                            if non_empty:
                                st.write(f"  Column {col_idx}: First values: {col_values[:5]}")
        
        # Parse tables to get driver data
        show_debug = st.checkbox("Show parsing debug info", value=True)
        with st.spinner("Parsing driver data..."):
            drivers = _parse_pdf_tables(tables, show_debug=show_debug, brand_id=pdf_brand_id)
        
        if not drivers:
            st.warning("No driver data found in the PDF. Please check the PDF format.")
            st.info("Expected format: Table with PRODUCT column containing entries like 'SMPS - Slim - 12V - 36W - 3Amp'")
            st.info("💡 **Tip:** Check the 'Debug: Raw Table Data' section above to see what was extracted from the PDF.")
            return
        
        # Display parsed data
        st.success(f"✅ Found {len(drivers)} driver(s) in the PDF")
        
        # Show preview with brand names instead of Bid
        with st.expander("Preview extracted data", expanded=True):
            # Replace Bid with Brand name for display
            preview_drivers = []
            for driver in drivers:
                preview_driver = driver.copy()
                bid = driver.get('Bid') or driver.get('bid')
                if bid and bid in bid_to_brand:
                    preview_driver['Brand'] = bid_to_brand[bid]
                    preview_driver.pop('Bid', None)
                    preview_driver.pop('bid', None)
                else:
                    preview_driver['Brand'] = f"Brand ID: {bid}" if bid else "No Brand"
                    preview_driver.pop('Bid', None)
                    preview_driver.pop('bid', None)
                preview_drivers.append(preview_driver)
            
            df = pd.DataFrame(preview_drivers)
            st.dataframe(df, use_container_width=True)
        
        # Insert button
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Insert into Database", type="primary", use_container_width=True):
                if not pdf_brand_id:
                    st.warning("⚠️ Please select a brand before inserting")
                else:
                    try:
                        with st.spinner("Inserting data into database..."):
                            result = insert_drivers_batch(drivers)
                            st.success(f"✅ Successfully inserted {len(drivers)} driver(s) into the database!")
                            st.balloons()
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error inserting data: {e}")
        
        with col2:
            if st.button("Clear Preview", use_container_width=True):
                st.rerun()

