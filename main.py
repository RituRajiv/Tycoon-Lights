# Main Streamlit application

import streamlit as st
import os
from config import PARTICULARS, VOLTAGE_OPTIONS, LED_OPTIONS
from utils import calculate_wattage
from pdf_generator import generate_pdf

# Page configuration for mobile and desktop
st.set_page_config(
    page_title="Tycoon Lights",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile responsiveness
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
    }
    .stButton>button {
        width: 100%;
    }
    .unit-toggle-container {
        display: flex;
        align-items: center;
        padding-top: 1.5rem;
    }
    /* Yellow button styling for Calculate button */
    button[data-testid*="calc_btn"] {
        background-color: #FFD700 !important;
        background: #FFD700 !important;
        background-image: none !important;
        color: #000000 !important;
        border: 1px solid #FFA500 !important;
        height: 48px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        min-width: 150px !important;
    }
    button[data-testid*="calc_btn"]:hover {
        background-color: #FFC700 !important;
        background: #FFC700 !important;
        border-color: #FF8C00 !important;
    }
    /* Column width controls */
    div[data-testid="column"]:has(button[data-testid*="calc_btn"]) {
        flex: 3 1 0% !important;
        min-width: 0% !important;
    }
    div[data-testid="column"]:has(button[data-testid*="add_btn"]) {
        flex: 1 1 0% !important;
        min-width: 0% !important;
    }
    /* Ensure selectbox and button fill their columns */
    .stSelectbox, .stSelectbox > div, .stSelectbox > div > div, .stSelectbox select {
        width: 100% !important;
        box-sizing: border-box !important;
    }
    .stSelectbox {
        display: block !important;
    }
    .stButton, .stButton > button {
        width: 100% !important;
        box-sizing: border-box !important;
    }
    .stButton {
        display: block !important;
    }
    /* Table cell borders - clean white borders on columns */
    .table-container div[data-testid="column"] {
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        padding: 10px 8px !important;
        margin: 0 !important;
        min-height: 50px !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    /* Table cell styling */
    div[data-testid="column"].table-cell {
        border: 2px solid #ffffff !important;
        padding: 8px !important;
        margin: 0 !important;
        min-height: 40px !important;
        box-sizing: border-box !important;
    }
    div[data-testid="column"].table-cell * {
        margin: 0 !important;
    }
    </style>
    <script>
    // Apply styling functions
    function applyStyling() {
        // Style calculate button
        const calcButton = document.querySelector('button[data-testid*="calc_btn"]');
        if (calcButton && !calcButton.dataset.yellowStyled) {
            calcButton.dataset.yellowStyled = 'true';
            calcButton.addEventListener('mouseenter', function(e) {
                e.target.style.setProperty('background-color', '#FFC700', 'important');
                e.target.style.setProperty('border-color', '#FF8C00', 'important');
            }, true);
            calcButton.addEventListener('mouseleave', function(e) {
                e.target.style.setProperty('background-color', '#FFD700', 'important');
                e.target.style.setProperty('border-color', '#FFA500', 'important');
            }, true);
        }
        
        // Set button column widths
        const addButton = document.querySelector('button[data-testid*="add_btn"]');
        if (calcButton && addButton) {
            const calcColumn = calcButton.closest('div[data-testid="column"]');
            const addColumn = addButton.closest('div[data-testid="column"]');
            if (calcColumn && addColumn) {
                calcColumn.style.setProperty('flex', '3 1 0%', 'important');
                addColumn.style.setProperty('flex', '1 1 0%', 'important');
            }
        }
        
        // Add table borders
        const editButtons = document.querySelectorAll('button[data-testid*="edit_"], button[data-testid*="delete_"]');
        editButtons.forEach(button => {
            const col = button.closest('div[data-testid="column"]');
            if (col && !col.classList.contains('table-cell')) {
                let parent = col.parentElement;
                let attempts = 0;
                while (parent && attempts < 7) {
                    const cols = parent.querySelectorAll('div[data-testid="column"]');
                    if (cols.length === 8 || cols.length === 2) {
                        cols.forEach(c => {
                            c.classList.add('table-cell');
                            c.style.setProperty('border', '2px solid #ffffff', 'important');
                            c.style.setProperty('padding', '8px', 'important');
                            c.style.setProperty('box-sizing', 'border-box', 'important');
                            c.style.setProperty('min-height', '40px', 'important');
                        });
                        break;
                    }
                    parent = parent.parentElement;
                    attempts++;
                }
            }
        });
    }
    
    // Initialize on load
    function init() {
        applyStyling();
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Watch for DOM changes
    const observer = new MutationObserver(applyStyling);
    observer.observe(document.body, { 
        childList: true, 
        subtree: true,
        attributes: true,
        attributeFilter: ['style', 'class']
    });
    </script>
""", unsafe_allow_html=True)

# Initialize session state
if 'table_data' not in st.session_state:
    st.session_state.table_data = []
if 'editing_row' not in st.session_state:
    st.session_state.editing_row = None

# Logo in center
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1 style='text-align: center;'>💡 Tycoon Lights</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# Dropdown for particulars
particular = st.selectbox("Select Particular", PARTICULARS, index=1)

# Brand name input - load from editing row if available
default_brand = ""
if st.session_state.editing_row is not None:
    default_brand = st.session_state.editing_row.get("Brand", "")
    if default_brand == "-":
        default_brand = ""
brand_name = st.text_input("Brand Name", value=default_brand, placeholder="Enter brand name")

# Driver section
if particular == "Drivers":
    # Load data from editing row if available
    default_length = ""
    default_is_feet = False
    default_voltage_index = 0
    default_led_index = 0
    default_discount = "0"
    
    if st.session_state.editing_row is not None:
        editing_row = st.session_state.editing_row
        
        # Parse Length field (format: "X Meter" or "X Feet")
        length_str = editing_row.get("Length", "")
        if length_str:
            parts = length_str.split()
            if len(parts) >= 2:
                try:
                    default_length = parts[0]
                    default_is_feet = parts[1].lower() == "feet"
                except:
                    pass
        
        # Parse Voltage field (format: "XV")
        voltage_str = editing_row.get("Voltage", "")
        if voltage_str:
            try:
                voltage_val = int(voltage_str.replace("V", ""))
                if voltage_val in VOLTAGE_OPTIONS:
                    default_voltage_index = VOLTAGE_OPTIONS.index(voltage_val)
            except:
                pass
        
        # Get LED count
        led_val = editing_row.get("LED", "")
        if led_val:
            try:
                if led_val in LED_OPTIONS:
                    default_led_index = LED_OPTIONS.index(led_val)
            except:
                pass
        
        # Get Discount
        discount_val = editing_row.get("Discount", "0")
        default_discount = discount_val if discount_val != "-" else "0"
    
    # Toggle for meter/feet and length input on same line
    current_is_feet = default_is_feet if st.session_state.editing_row is not None else st.session_state.get("unit_toggle", False)
    toggle_label = "Feet" if current_is_feet else "Meter"
    
    # Create columns for horizontal alignment - length column matches voltage column width
    col_length, col_unit = st.columns([1, 1])
    with col_length:
        length_input = st.text_input(f"Length ({toggle_label})", value=default_length, placeholder="Enter length", key=f"length_{toggle_label}")
    with col_unit:
        st.markdown('<div class="unit-toggle-container">', unsafe_allow_html=True)
        is_feet = st.toggle(toggle_label, value=current_is_feet, key="unit_toggle")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Determine unit after toggle is set
    unit = "Feet" if is_feet else "Meter"
    
    # Validate and convert length input to integer
    length = None
    if length_input:
        try:
            # Try to convert to integer directly
            length = int(length_input)
            if length < 0:
                st.warning("Length must be a positive integer")
                length = None
        except ValueError:
            st.warning("Please enter a valid integer for length")
            length = None
    
    # Voltage and LED dropdowns on same line
    col_voltage, col_led = st.columns(2)
    with col_voltage:
        voltage = st.selectbox("Voltage", VOLTAGE_OPTIONS, index=default_voltage_index)
    with col_led:
        led_count = st.selectbox("LED", LED_OPTIONS, index=default_led_index)
    
    # Discount text box with default value of 0
    discount = st.text_input("Discount", value=default_discount, placeholder="Enter discount")
    
    # Calculate and Add to Table buttons on same line
    col_calc, col_add = st.columns([1, 1])
    with col_calc:
        calculate_clicked = st.button("Calculate", type="secondary", key="calc_btn")
    with col_add:
        button_text = "Update Table" if st.session_state.editing_row is not None else "Add to Table"
        add_clicked = st.button(button_text, type="secondary", key="add_btn")
    
    # Calculate button logic
    if calculate_clicked:
        if length is not None and length > 0 and led_count > 0:
            wattage = calculate_wattage(length, led_count, unit)
            st.info(f"**Calculated Wattage: {wattage} W** (Formula: {length} {unit.lower()} × {led_count/10} = {wattage} W)")
            # Store wattage and calculation parameters in session state
            st.session_state.calculated_wattage = wattage
            st.session_state.calc_length = length
            st.session_state.calc_led_count = led_count
            st.session_state.calc_unit = unit
        else:
            st.warning("Please enter a valid length (integer) and select LED count")
    
    # Add/Update button logic
    if add_clicked:
        if length is not None and length > 0 and led_count > 0:
            # Use calculated wattage from session state if inputs match, otherwise calculate on the fly
            if ('calculated_wattage' in st.session_state and 
                st.session_state.calculated_wattage and
                'calc_length' in st.session_state and
                'calc_led_count' in st.session_state and
                'calc_unit' in st.session_state and
                st.session_state.calc_length == length and
                st.session_state.calc_led_count == led_count and
                st.session_state.calc_unit == unit):
                wattage = st.session_state.calculated_wattage
            else:
                wattage = calculate_wattage(length, led_count, unit)
            
            updated_row = {
                "Brand": brand_name if brand_name else "-",
                "Length": f"{length} {unit}",
                "Voltage": f"{voltage}V",
                "LED": led_count,
                "Wattage": f"{wattage} W",
                "Discount": discount if discount else "-"
            }
            
            # Update existing row or add new row
            if st.session_state.editing_row is not None:
                # Find and update the row
                for i, row in enumerate(st.session_state.table_data):
                    if row == st.session_state.editing_row:
                        st.session_state.table_data[i] = updated_row
                        break
                st.success("Updated table!")
                st.session_state.editing_row = None  # Clear editing state
            else:
                st.session_state.table_data.append(updated_row)
                st.success("Added to table!")
            st.rerun()
        else:
            st.warning("Please enter a valid length (integer) and select LED count")

elif particular == "LED strips":
    st.info("LED strips functionality coming soon...")

# Display table
if st.session_state.table_data:
    # Display table with edit and delete buttons
    st.markdown("### Table")
    # Add wrapper div for table styling
    st.markdown('<div class="table-container">', unsafe_allow_html=True)
    
    # Display header row
    # Column widths: [#: 1 (min), Brand: 2, Length: 2, Voltage: 2, LED: 2, Wattage: 2, Discount: 2, Actions: 3]
    header_cols = st.columns([1, 2, 2, 2, 2, 2, 2, 3])
    headers = ["#", "Brand", "Length", "Voltage", "LED", "Wattage", "Discount", "Actions"]
    for i, header in enumerate(headers):
        with header_cols[i]:
            st.markdown(f"**{header}**")
    
    # Create a custom table display with buttons
    for idx, row in enumerate(st.session_state.table_data):
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 2, 2, 2, 2, 2, 2, 3])
        
        with col1:
            st.write(f"{idx + 1}")
        with col2:
            st.write(row.get("Brand", "-"))
        with col3:
            st.write(row.get("Length", "-"))
        with col4:
            st.write(row.get("Voltage", "-"))
        with col5:
            st.write(row.get("LED", "-"))
        with col6:
            st.write(row.get("Wattage", "-"))
        with col7:
            st.write(row.get("Discount", "-"))
        with col8:
            col_edit, col_del = st.columns(2)
            with col_edit:
                if st.button("Edit", key=f"edit_{idx}", type="secondary"):
                    st.session_state.editing_row = row
                    st.rerun()
            with col_del:
                if st.button("Delete", key=f"delete_{idx}", type="secondary"):
                    st.session_state.table_data.pop(idx)
                    # Clear editing_row if it was the deleted row
                    if st.session_state.editing_row == row:
                        st.session_state.editing_row = None
                    st.success("Row deleted!")
                    st.rerun()
    
    # Close wrapper div
    st.markdown('</div>', unsafe_allow_html=True)
    
    # PDF generation button
    if st.button("Convert to PDF", type="secondary"):
        filename = generate_pdf(st.session_state.table_data)
        with open(filename, "rb") as pdf_file:
            st.download_button(
                label="Download PDF",
                data=pdf_file.read(),
                file_name=filename,
                mime="application/pdf"
            )
        os.remove(filename)