# AI-Powered Site Reporting & Analysis System

## Project Overview

This project implements an intelligent system designed to automate and enhance construction site reporting. By leveraging advanced Large Language Models (LLMs) and a robust data pipeline, it transforms unstructured daily observations into actionable, categorized insights and generates comprehensive management reports.

## Core Features (AI Focus)

  * **Intelligent Observation Classification:** Utilizes a **fine-tuned Large Language Model (LLM)** to automatically classify raw, unstructured site comments and observations into predefined categories (e.g., Safety, Quality) and relevant task groups. This brings structure to qualitative data.
  * **LLM-Driven Report Summarization:** Employs an LLM to dynamically generate concise, human-readable daily reports or comprehensive summaries based on classified site data, streamlining the reporting process for management review.
  * **Contextual Analysis via RAG (Retrieval Augmented Generation):** Incorporates a dedicated pipeline for contextual analysis, preparing and feeding relevant, indexed historical data to the LLM. This **Retrieval Augmented Generation (RAG)** approach enhances the LLM's understanding and allows for more accurate and insightful report generation.
  * **Structured Data Persistence:** All classified site observations are stored persistently in a structured **JSON format**, enabling historical analysis, data mining, and flexible programmatic access for integration with other systems.
*Flowchart for app*
![Classification](https://github.com/4maan4hmed/AI-powered-Site-Manager/blob/main/images/flowchart.png)

## Technologies Used

  * **Python:** The core programming language for the entire system.
  * **Large Language Models (LLM):** At the heart of classification and summarization (e.g., Mistral, Llama, via a local API server).
  * **Fine-tuning:** Customization of LLMs for specialized site observation classification.
  * **Retrieval Augmented Generation (RAG):** For providing contextual data to the LLM.
  * **Streamlit:** For building interactive web-based user interfaces.
  * **JSON:** For structured data storage and interchange.
  * **REST APIs:** For communication with the local LLM inference server.
  * **Pandas:** For efficient data manipulation and analysis within the application.

## Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

  * Python 3.8+
  * `pip` (Python package installer)
  * A running **Large Language Model (LLM) server** accessible via a REST API (e.g., `llama.cpp` server configured to run Mistral or a similar model). Ensure it's accessible at `http://127.0.0.1:8080/completion` or update the `LLAMA_URL` in the scripts accordingly.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/4maan4hmed/AI-powered-Site-Manager/
    cd AI-powered-Site-Manager
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### Running the LLM Servers

This project utilizes two LLM servers: one for the base Mistral model and another for your fine-tuned model.

1.  **Download the Fine-Tuned Model from Hugging Face:**
    [finetuned Model](https://huggingface.co/4maan4hmad/Mistral-finetuned-sitemanager-v2.0)
    or
     run:
    ```bash
    # Still inside models/
    wget https://huggingface.co/4maan4hmad/Mistral-finetuned-sitemanager-v2.0/blob/main/unsloth.Q4_K_M.gguf
    ```

3.  **Run Two LLM Servers:**

    ```bash
    # Terminal 1: Base Mistral
    ./server -m models/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
      --host 0.0.0.0 --port 8080 --n-ctx 2048 --temp 0.5

    # Terminal 2: Your Finetuned Model
    ./server -m models/mistral-finetuned-sitemanager.Q4_K_M.gguf \
      --host 0.0.0.0 --port 8081 --n-ctx 2048 --temp 0.5
    ```

    Verify the servers are running and accessible at `http://127.0.0.1:8080/completion` and `http://127.0.0.1:8081/completion` respectively.

    Or run them one at a time, UI.py run finetuned mode and for Report use any model of your choice, dont forget to keep the correct ports.

## Usage

The project consists of two main Streamlit applications: one for data entry and classification, and another for generating reports.

### 1\. Data Entry & Classification App

This application allows users to submit site observations, which are then classified by the LLM and stored.

  * **Run the app:**

    ```bash
    streamlit run UI.py
    ```
  * **How to use:**

    1.  Enter an Employee ID and your observation/comment.
    2.  Click "Submit Comment for Classification."
    3.  Review the AI's classification (Type, Task Group).
    4.  Click "Add to Report" to save the classified data to `ground_site_report.json`.

#### UI Example: Data Entry & Classification


*Giving input to the model*
![Classification](https://github.com/4maan4hmed/AI-powered-Site-Manager/blob/main/images/UI%201.png)

*Classification output from the finetuned Mistral Model*
![Output](https://github.com/4maan4hmed/AI-powered-Site-Manager/blob/main/images/UI%20Output.png)

*Previous Outputs saved in CSV file*
![Previous Output](https://github.com/4maan4hmed/AI-powered-Site-Manager/blob/main/images/Previous%20Output.png)


### 2\. Report Generation App

This application reads from the stored `ground_site_report.json` and uses the LLM to generate daily or comprehensive summaries.

  * **Run the app:**

    ```bash
    streamlit run summarize.py
    ```

  * **How to use:**

    1.  Select "Summary for a specific date" and choose a date, or select "Full Summary of all data."
    2.  Click "Generate Report."
    3.  The LLM will process the relevant observations and generate a concise report, which will be displayed and saved as a `.txt` file in the `generated_reports` directory.

#### UI Example: Date Summarization

![Model Diagram](https://github.com/4maan4hmed/AI-powered-Site-Manager/blob/main/images/Screenshot%20(559).png)


#### Example Work / Generated Report

Here's an example of a daily report generated by the system:
![Generated Report](https://github.com/4maan4hmed/AI-powered-Site-Manager/blob/main/images/Generated%20report.png)

### 3. Report-Based Question Answering (RAG)

This module allows users to ask intelligent questions based on previously generated reports. It uses a **Retrieval Augmented Generation (RAG)** approach, where past `.txt` reports are indexed and relevant chunks are fed to the LLM to answer queries in context.

* **Run the notebook:**

  [Report\_QA\_RAG.ipynb](https://github.com/4maan4hmed/AI-powered-Site-Manager/blob/main/StreamlitUI/rag_ollama_chatbot.ipynb)

* **How to use:**

  1. Ensure you have some reports generated in the `Summarise Report/` directory.
  2. Open the notebook and run all cells.
  3. Type your question related to the reports (e.g., safety issues, quality insights).
  4. The notebook retrieves the most relevant report sections and passes them to the LLM to generate a detailed answer.

# Example: RAG-based QA on Generated Reports

*Input Query & Retrieved Chunks*
![QA Input](https://github.com/4maan4hmed/AI-powered-Site-Manager/blob/main/images/rag%20input-retrievied%20data.png)

*LLM Answer Based on Context*
![QA Output](https://github.com/4maan4hmed/AI-powered-Site-Manager/blob/main/images/RAG-output.png)

---

## Project Structure

```
.
├── UI.py         # Streamlit app for submitting and classifying comments
├── summarize.py   # Streamlit app for generating daily/full reports
├── ground_site_report.json   # Persistent storage for all classified observations
├── Summarise Report/        # Directory where generated text reports are saved
│   ├──YYYY-MM-DD_report.txt
│   └── full_report_YYYYMMDD_HHMMSS.txt
├── rag_ollama_chatbot.ipynb
└── requirements.txt          # Python dependencies
```

## Contributing

Feel free to fork this repository, open issues, or submit pull requests.

## Contact

[Amaan Ahmad] - (https://www.linkedin.com/in/amaan-ahmad-051585208/)
