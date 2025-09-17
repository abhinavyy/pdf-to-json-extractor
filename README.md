# 📄 PDF to Structured JSON Extractor

[](https://www.python.org/) [](https://streamlit.io/) [](https://www.google.com/search?q=./LICENSE)

An intelligent tool that transforms unstructured PDFs into developer-friendly JSON. It intelligently parses documents to identify paragraphs, tables, and charts, preserving the document's hierarchical structure by recognizing sections and sub-sections.

The project features a simple web interface built with Streamlit for easy file uploads, as well as a command-line interface (CLI) for programmatic use.

## ✨ Features

  * **Page-Level Hierarchy**: Preserves the structure of the document page by page.
  * **Content-Type Identification**: Automatically captures and labels different data types:
      * 📝 Paragraphs (including headings)
      * 📊 Tables
      * 🖼️ Charts & Images
  * **Hierarchical Section Detection**: Uses font styles and sizes to heuristically identify headings, automatically assigning section and sub-section context to the extracted content.
  * **Clean & Readable Output**: Text is cleaned and formatted for readability, and tables are extracted into clean lists of lists.
  * **User-Friendly Web App**: A simple Streamlit interface allows you to upload a PDF and download the resulting JSON with a click.
  * **Developer-Friendly CLI**: A command-line interface is available for batch processing or integration into other workflows.

## 📂 Project Structure

```
.
├── app.py                  # The Streamlit web application
├── main.py                 # The command-line interface script
├── requirements.txt        # Project dependencies
├── README.md               # This file
├── data/                   # Folder for sample input PDFs
├── output/                 # Folder for generated JSON outputs from the CLI
├── uploads/                # Temporary folder for web app uploads
└── src/
    ├── __init__.py
    └── parser.py           # Core PDF parsing class and logic
```

## ⚙️ Setup and Installation

Follow these steps to get the project running on your local machine.

### 1\. Prerequisites

  * Python 3.8+
  * Git
  * **(Optional but Recommended) Ghostscript**: [Camelot](https://camelot-py.readthedocs.io/en/master/user/install-deps.html) may require Ghostscript for some PDFs. It's a good idea to install it to prevent potential issues.

### 2\. Clone the Repository

Open your terminal and clone the project repository:

```bash
git clone https://github.com/abhinavyy/pdf-to-json-extractor.git
cd pdf-to-json-extractor
```

### 3\. Create and Activate a Virtual Environment

It's highly recommended to use a virtual environment to keep project dependencies isolated.

**On Windows:**

```bash
# Create the virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate
```

**On macOS / Linux:**

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

### 4\. Install Dependencies

Install all the required Python libraries using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

-----

## 🚀 How to Run

You can run the application in two ways. The web app is recommended for general use.

### Option 1: Run the Streamlit Web App (Recommended)

This is the easiest way to use the parser.

1.  Make sure your virtual environment is activated.
2.  In your terminal, run the following command from the project root directory:
    ```bash
    streamlit run app.py
    ```
3.  Your web browser will automatically open with the application running.
4.  Simply drag and drop your PDF file into the uploader and download the resulting JSON.

### Option 2: Run via the Command Line (For Developers)

This method is useful for testing, debugging, or integrating the parser into automated workflows.

1.  Make sure your virtual environment is activated.

2.  Run the `main.py` script with arguments for the input and output file paths.

    **Syntax:**
    **Example:**

    ```bash
    python main.py --input data/sample_given.pdf --output output/sample_output.json
    ```

3.  After the script finishes, you will find the generated JSON file inside the `output/` directory.
