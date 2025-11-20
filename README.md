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
8. Click **"Add to Quotation"** to save the entry

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

## Deployment to Streamlit Cloud

### Prerequisites

1. **GitHub Account**: Your code needs to be in a GitHub repository
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io) (free)
3. **Supabase Credentials**: You'll need your Supabase URL and API keys

### Step-by-Step Deployment

#### 1. Push Your Code to GitHub

If you haven't already, initialize git and push to GitHub:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit your changes
git commit -m "Initial commit"

# Create a repository on GitHub, then add remote and push
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

**Important**: Make sure your `.gitignore` file includes `.env` so you don't commit sensitive credentials!

#### 2. Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Select your repository** from the dropdown
5. **Choose the branch** (usually `main`)
6. **Set the main file path**: `main.py`
7. **Click "Deploy!"**

#### 3. Configure Environment Variables

After deployment, you need to add your Supabase credentials:

1. **Go to your app's settings** (click the "⋮" menu → "Settings")
2. **Navigate to "Secrets"** tab
3. **Add the following secrets**:

```toml
SUPABASE_URL = "your-supabase-project-url"
SUPABASE_KEY = "your-supabase-anon-key"
SUPABASE_SERVICE_ROLE_KEY = "your-supabase-service-role-key"
```

**How to find your Supabase credentials:**
- Go to your Supabase project dashboard
- Navigate to **Settings** → **API**
- Copy the **Project URL** → use as `SUPABASE_URL`
- Copy the **anon/public key** → use as `SUPABASE_KEY`
- Copy the **service_role key** → use as `SUPABASE_SERVICE_ROLE_KEY` (keep this secret!)

4. **Click "Save"** - Streamlit will automatically restart your app

#### 4. Access Your Deployed App

Once deployed, your app will be available at:
```
https://YOUR_APP_NAME.streamlit.app
```

You can also find the URL in your Streamlit Cloud dashboard.

### Troubleshooting

**App won't start:**
- Check that all dependencies are in `requirements.txt`
- Verify environment variables are set correctly
- Check the logs in Streamlit Cloud dashboard

**Database connection errors:**
- Verify your Supabase credentials are correct
- Check that your Supabase project is active
- Ensure your Supabase database tables exist (`Particulars`, `Brand`, `Drivers`)

**Import errors:**
- Make sure all Python files are in the repository
- Check that `components/__init__.py` exists
- Verify all imports in `main.py` are correct

### Updating Your Deployed App

To update your deployed app:

1. **Make changes** to your code locally
2. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "Your update message"
   git push
   ```
3. **Streamlit Cloud will automatically detect** the changes and redeploy (usually takes 1-2 minutes)

### Alternative: Manual Deployment

If you prefer to deploy manually or use a different platform:

1. **Set up a server** (AWS, Heroku, DigitalOcean, etc.)
2. **Install Python 3.12+** and dependencies
3. **Set environment variables** in your server's configuration
4. **Run**: `streamlit run main.py --server.port 8501`

## Notes

- The application stores data in session state, so data will be lost when you refresh the page
- PDF files are temporarily created and automatically deleted after download
- For better performance, consider installing the Watchdog module: `pip install watchdog`
- **Never commit `.env` files** - use Streamlit Cloud secrets or your platform's environment variable system

## License

This project is for internal use by Tycoon Lights.

