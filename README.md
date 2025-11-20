# 💡 Tycoon Lights - LED Driver Calculator

A Streamlit web application for calculating LED driver wattage and managing driver specifications. This tool helps you calculate the required wattage for LED drivers based on length and LED count, with support for both meters and feet.

## Features

- **Wattage Calculation**: Calculate LED driver wattage based on length and LED count
- **Unit Conversion**: Support for both meters and feet
- **Driver Management**: Add, edit, and delete driver entries in a table
- **PDF Export**: Generate PDF reports from your driver calculations
- **Mobile Responsive**: Optimized for both desktop and mobile devices

## Requirements

- Python 3.12+
- Streamlit 1.51.0
- ReportLab 4.4.4
- Pandas 2.3.3

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd TycoonLights
   ```

2. **Create a virtual environment (if not already created):**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Activate the virtual environment** (if not already activated):
   ```bash
   source venv/bin/activate
   ```

2. **Run the Streamlit app:**
   ```bash
   streamlit run main.py
   ```

3. **Open your browser:**
   The application will automatically open in your default browser at `http://localhost:8501`

## Usage

### Calculating Wattage

1. Select **"Drivers"** from the Particular dropdown
2. Enter the **Brand Name** (optional)
3. Enter the **Length** in meters or feet (use the toggle to switch units)
4. Select the **Voltage** (12V, 24V, or 48V)
5. Select the **LED Count** (120, 180, or 240)
6. Enter **Discount** percentage (optional, defaults to 0)
7. Click **"Calculate"** to see the wattage calculation
8. Click **"Add to Table"** to save the entry

### Formula

The wattage is calculated using the formula:
```
Wattage = Length (in meters) × (LED Count / 10)
```

If the length is entered in feet, it's automatically converted to meters before calculation.

### Managing Entries

- **Edit**: Click the "Edit" button on any row to modify its values
- **Delete**: Click the "Delete" button to remove an entry
- **Export to PDF**: Click "Convert to PDF" to generate a downloadable PDF report

## Project Structure

```
TycoonLights/
├── main.py              # Main Streamlit application
├── config.py            # Configuration constants (voltage options, LED options)
├── utils.py             # Utility functions (wattage calculation)
├── pdf_generator.py     # PDF generation functionality
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Configuration

You can modify the following constants in `config.py`:

- `PARTICULARS`: Available product types (currently: "LED strips", "Drivers")
- `VOLTAGE_OPTIONS`: Available voltage options (default: [12, 24, 48])
- `LED_OPTIONS`: Available LED count options (default: [120, 180, 240])

## Technologies Used

- **Streamlit**: Web framework for building the user interface
- **ReportLab**: PDF generation library
- **Pandas**: Data manipulation for table operations

## Notes

- The application stores data in session state, so data will be lost when you refresh the page
- PDF files are temporarily created and automatically deleted after download
- For better performance, consider installing the Watchdog module: `pip install watchdog`

## License

This project is for internal use by Tycoon Lights.

