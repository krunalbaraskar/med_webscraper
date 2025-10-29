# Adalimumab Tender Scrapers

This repository contains Python scripts to scrape European public procurement websites for tenders related to the pharmaceutical product "adalimumab".

Two scrapers are included:

1.  **Spanish Government Scraper (`spanish_scraper.ipynb`)**:
    * Targets: `https://contrataciondelestado.es/wps/portal/plataforma`
    * Runs in a Jupyter Notebook with four sequential steps: Scrape URLs -> Download HTMLs -> Parse & Translate -> Clean Data.
2.  **TED Europa Scraper (`ted_extract_html_pages.py`)**:
    * Targets: `https://ted.europa.eu/`
    * A Python script that searches for "adalimumab" notices and downloads the corresponding detail page HTMLs. *Note: A separate script (like `parse_ted_html_gemini.py`, not included here) is needed to parse these downloaded HTMLs.*

## Prerequisites

* Windows OS
* Python 3.x (added to PATH)
* Google Chrome Browser
* Matching ChromeDriver executable

## Setup (Common for Both Scrapers)

1.  **Get Files:** Clone or download the repository files (including `.ipynb`, `.py`, and `setup_env.bat`).
2.  **Download ChromeDriver:**
    * Find your Chrome version (`chrome://settings/help`).
    * Download the matching `chromedriver.exe` (win64) from the [Chrome for Testing dashboard](https://googlechromelabs.github.io/chrome-for-testing/). 
    * Unzip and place `chromedriver.exe` in the **same directory** as the script files.
3.  **Install Dependencies:**
    * Open Command Prompt (cmd) or PowerShell in the project directory.
    * Run: `.\setup_env.bat` (This creates a virtual environment named `venv_scraper` and installs required packages like `jupyter`, `selenium`, `pandas`, `beautifulsoup4`, `requests`, `deep-translator`, `tqdm`, `lxml`).

## Running the Spanish Scraper (`spanish_scraper.ipynb`)

**Important:** The notebook cells must be run one after another.

1.  **Activate Environment:**
    * **CMD:** `venv_scraper\Scripts\activate.bat`
    * **PowerShell:** `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` then `.\venv_scraper\Scripts\Activate.ps1`
    * *(Prompt should show `(venv_scraper)`)*
2.  **Configure ChromeDriver Path:**
    * Open `spanish_scraper.ipynb`.
    * In the **first code cell**, change `CHROME_DRIVER_PATH = None` to `CHROME_DRIVER_PATH = "chromedriver.exe"`.
    * Save the notebook.
3.  **Start Jupyter:**
    * In the activated terminal, run: `jupyter notebook spanish_scraper.ipynb`
4.  **Run Cells Sequentially in Jupyter:**
    * Execute Cell 1, wait for completion (`collected_adalimumab_urls.csv`).
    * Execute Cell 2, wait for completion (`docs/`).
    * Execute Cell 3, wait for completion (`tender_data_final.csv`).
    * Execute Cell 4 (`tender_data_final_cleaned.csv`).

## Running the TED Europa Scraper (`ted_extract_html_pages.py`)

1.  **Activate Environment:** (See step 1 above if not already active).
2.  **Configure ChromeDriver Path:**
    * Open `ted_extract_html_pages.py` in a text editor.
    * Find the line `CHROME_DRIVER_PATH = "chromedriver.exe"` (or similar) and ensure it correctly points to your `chromedriver.exe`.
    * Save the file.
3.  **Run the Script:**
    * In the activated terminal, run: `python ted_extract_html_pages.py`
    * The script will scrape the TED website and save HTML files to the `ted_html_pages` folder.

## Output Files

**Spanish Scraper:**

* `collected_adalimumab_urls.csv`
* `docs/` (folder with HTMLs and other PDFs)
* `saved_docs_map.csv`
* `tender_data_final.csv`
* `tender_data_final_cleaned.csv` (Final Output)

**TED Europa Scraper:**

* `ted_html_pages/` (folder with downloaded HTML detail pages)
