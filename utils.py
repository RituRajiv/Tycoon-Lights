# Utility functions for calculations

def calculate_wattage(length, led_count, unit="Meter"):
    """Calculate wattage based on length and LED count"""
    if unit == "Feet":
        # Convert feet to meters (1 meter = 3.28084 feet)
        length = length / 3.28084
    
    # Calculate: length * (LED count / 10)
    # Example: 16 meter * (240/10) = 16 * 24 = 384 watt
    wattage = length * (led_count / 10)
    return round(wattage, 2)

