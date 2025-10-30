# Adalimumab Tender Scrapers

This repository contains Python scripts to scrape European public procurement websites for tenders related to the pharmaceutical product "adalimumab".

The project includes two main scrapers, both of which run in Jupyter Notebooks:

1.  **Spanish Government Scraper (`spanish_scraper.ipynb`)**:
    * **Target:** `https://contrataciondelestado.es/wps/portal/plataforma`
    * **Process:** A four-step notebook that sequentially scrapes tender URLs, downloads all associated tender documents (HTML, PDF), parses the HTMLs, translates the content, and cleans the final data.

2.  **TED Europa Scraper (`ted_extract_tender_info_py.ipynb`)**:
    * **Target:** `https://ted.europa.eu/`
    * **Process:** A multi-stage notebook that first scrapes and downloads all tender HTML pages, then parses those local HTMLs to extract and translate data, and finally cleans the extracted data into a structured CSV.

## Prerequisites

* Windows OS
* Python 3.x (added to PATH)
* Google Chrome Browser
* Matching ChromeDriver executable

## Setup (Common for Both Scrapers)

1.  **Get Files:** Clone or download the repository files (including `.ipynb`, `.py`, and `setup_env.bat`).
2.  **Download ChromeDriver:**
    * Find your Chrome version (Go to `chrome://settings/help`).
    * Download the matching `chromedriver.exe` (win64) from the [Chrome for Testing dashboard](https://googlechromelabs.github.io/chrome-for-testing/).
    * Unzip and place `chromedriver.exe` in the **same directory** as the script files.
3.  **Install Dependencies:**
    * Open Command Prompt (cmd) or PowerShell in the project directory.
    * Run: `.\setup_env.bat`
    * This batch script creates a virtual environment named `venv_scraper` and installs all required packages: `jupyter`, `selenium`, `pandas`, `beautifulsoup4`, `requests`, `deep-translator`, `tqdm`, and `lxml`.

## Running the Spanish Scraper (`spanish_scraper.ipynb`)

**Important:** The notebook cells must be run one after another.

1.  **Activate Environment:**
    * **CMD:** `venv_scraper\Scripts\activate.bat`
    * **PowerShell:** `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` (run once), then `.\venv_scraper\Scripts\Activate.ps1`
    * *(Your terminal prompt should now show `(venv_scraper)`)*
2.  **Configure ChromeDriver Path:**
    * Open `spanish_scraper.ipynb`.
    * In the **first code cell**, change `CHROME_DRIVER_PATH = None` to `CHROME_DRIVER_PATH = "chromedriver.exe"`.
    * Save the notebook.
3.  **Start Jupyter:**
    * In the activated terminal, run: `jupyter notebook spanish_scraper.ipynb`
4.  **Run Cells Sequentially in Jupyter:**
    * Execute **Cell 1** (Scrape URLs) and wait for it to complete.
        * *Output: `collected_adalimumab_urls.csv`*
    * Execute **Cell 2** (Download HTMLs) and wait for it to complete.
        * *Output: `docs/` folder*
    * Execute **Cell 3** (Parse & Translate) and wait for it to complete.
        * *Output: `tender_data_final.csv`*
    * Execute **Cell 4** (Clean Data).
        * *Output: `tender_data_final_cleaned.csv`*

## Running the TED Europa Scraper (`ted_extract_tender_info_py.ipynb`)

**Important:** The notebook cells must be run one after another.

1.  **Activate Environment:** (See step 1 above if not already active).
2.  **Configure Paths in the Notebook:**
    * Open `ted_extract_tender_info_py.ipynb`.
    * **In Cell 2 (Scraper):** Change `CHROME_DRIVER_PATH = None` to `CHROME_DRIVER_PATH = "chromedriver.exe"`.
    * **In Cell 3 (Parser):** This is a critical step. You must tell the parser where to find the HTMLs downloaded by Cell 2.
        * Find the line: `HTML_FOLDER_PATH = '/content/med_webscraper/ted_html_pages'`
        * Change it to: `HTML_FOLDER_PATH = 'ted_html_pages'`
    * Save the notebook.
3.  **Start Jupyter:**
    * In the activated terminal, run: `jupyter notebook ted_extract_tender_info_py.ipynb`
4.  **Run Cells Sequentially in Jupyter:**
    * Execute **Cell 1** (`!pip install...`) to ensure all dependencies are installed.
    * Execute **Cell 2** (Main Scraper Function) and wait for it to complete. This scrapes the website and downloads all HTMLs.
        * *Output: `ted_html_pages/` folder*
    * Execute **Cell 3** (Main Execution) and wait for it to complete. This parses all local HTMLs, translates text, and saves the raw data.
        * *Output: `tender_output.csv`*
    * Execute **Cell 6** (Cleaning) to clean and finalize the data.
        * *Output: `ted_processed_tender_output.csv`*

## Output Files

**Spanish Scraper:**

* `collected_adalimumab_urls.csv`: List of all tender URLs found.
* `docs/`: Folder containing all downloaded HTML and PDF documents.
* `saved_docs_map.csv`: A map linking tenders to their saved files.
* `tender_data_final.csv`: Raw, parsed, and translated data.
* `tender_data_final_cleaned.csv`: **(Final Output)** The cleaned, structured data.

**TED Europa Scraper:**

* `ted_html_pages/`: Folder containing all downloaded HTML detail pages.
* `tender_output.csv`: Raw, parsed, and translated data from the HTMLs.
* `ted_processed_tender_output.csv`: **(Final Output)** The cleaned, filtered, and structured data.
