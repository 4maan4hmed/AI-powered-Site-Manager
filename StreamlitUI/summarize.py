import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import os
import subprocess

# --- Configuration ---

#running the Mistral model server

subprocess.Popen([r"D:\Projects\Lattice interview 2\model run\mistral_7b.bat"], shell=True)

st.set_page_config(layout="wide")
st.title("Ground Site Work - Daily Report Generator")

LLAMA_URL = "http://127.0.0.1:8080/completion"
REPORT_DATA_FILE = "ground_site_report.json" # Source of raw data
OUTPUT_REPORTS_DIR = "D:/Projects/Lattice interview 2/Summarise Report" # Directory for generated text reports
import os

os.system("D:/Projects/Lattice interview 2/model run/mistral_7b.bat")

# --- Helper Functions for File Operations ---

def load_all_report_data_from_json_file():
    """Loads all report data from the main JSON file as a single JSON array."""
    if os.path.exists(REPORT_DATA_FILE):
        try:
            with open(REPORT_DATA_FILE, 'r') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    st.warning(f"Warning: {REPORT_DATA_FILE} does not contain a JSON array. Returning empty.")
                    return []
            return data
        except json.JSONDecodeError:
            st.error(f"Error decoding JSON from {REPORT_DATA_FILE}. File might be corrupted or not a valid JSON array.")
            return []
        except Exception as e:
            st.error(f"Error reading {REPORT_DATA_FILE}: {e}")
            return []
    return [] # Return empty list if file doesn't exist

def save_generated_report_to_file(filename, content):
    """Saves the generated report content to a text file within the reports directory."""
    os.makedirs(OUTPUT_REPORTS_DIR, exist_ok=True) # Create directory if it doesn't exist
    file_path = os.path.join(OUTPUT_REPORTS_DIR, filename)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, file_path
    except Exception as e:
        st.error(f"Error saving report to file {file_path}: {e}")
        return False, None

# --- Session State Initialization ---
if "generated_report_text" not in st.session_state:
    st.session_state.generated_report_text = ""
if "report_file_path" not in st.session_state:
    st.session_state.report_file_path = ""

# --- Report Generation Interface ---
st.header("Generate Daily / Full Report")

# Data selection option
report_scope = st.radio(
    "Select Report Scope:",
    ("Summary for a specific date", "Full Summary of all data"),
    key="report_scope"
)

selected_date = None
if report_scope == "Summary for a specific date":
    selected_date = st.date_input("Select Date:", datetime.today(), key="report_date")

if st.button("Generate Report"):
    all_site_data = load_all_report_data_from_json_file()

    if not all_site_data:
        st.warning(f"No data found in {REPORT_DATA_FILE} to generate a report.")
    else:
        filtered_data = []
        report_title_suffix = ""

        if report_scope == "Summary for a specific date" and selected_date:
            # Convert selected_date to string format matching the Timestamp in JSON
            target_date_str = selected_date.strftime("%Y-%m-%d")
            filtered_data = [
                entry for entry in all_site_data
                if entry.get("Timestamp", "").startswith(target_date_str)
            ]
            report_title_suffix = f" for {target_date_str}"
            output_filename = f"{target_date_str}_ground_site_report.txt"
        else: # Full Summary
            filtered_data = all_site_data
            report_title_suffix = " (All Data)"
            output_filename = f"full_ground_site_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        if not filtered_data:
            st.info(f"No entries found for the selected scope: {report_title_suffix.strip()} to generate a report.")
            st.session_state.generated_report_text = ""
            st.session_state.report_file_path = ""
        else:
            # Prepare data for the AI prompt
            # Convert list of dicts to a more readable string format for the AI
            data_for_ai = "\n".join([
                f"- Employee ID: {entry.get('Employee ID')}, Type: {entry.get('Type')}, Task Group: {entry.get('Task Group')}, Comment: \"{entry.get('Original Comment')}\", Timestamp: {entry.get('Timestamp')}"
                for entry in filtered_data
            ])

            # Construct the prompt for the Mistral model
            prompt = f"""
<|im_start|> You: You are an expert site manager report writer.
Based on the following ground site observations, write a concise and informative daily report.
Focus on summarizing the types of issues, identifying key task groups involved, and noting any significant observations.
The report should be suitable for a management review.

Observations:
{data_for_ai} <|im_end|>
<|im_start|> assistant
"""
            payload = {
                "prompt": prompt,
                "temperature": 0.7, 
                "n_predict": 512,  # for longer reports
                "top_k": 50,  # Adjusted for better diversity
                "stream": False,
                "stop": ["<|im_end|>"],
            }

            st.info("Generating report... Please wait.")
            try:
                response = requests.post(LLAMA_URL, json=payload, timeout=120) # Increased timeout
                response.raise_for_status()
                result = response.json()
                ai_generated_report = result.get("content", "").strip()

                st.session_state.generated_report_text = ai_generated_report
                success, file_path = save_generated_report_to_file(output_filename, ai_generated_report)
                if success:
                    st.session_state.report_file_path = file_path
                    st.success(f"Report generated and saved to: {file_path}")
                else:
                    st.error("Failed to save report to file.")

            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to AI model: {e}. Please ensure the model server is running at {LLAMA_URL}.")
                st.session_state.generated_report_text = ""
                st.session_state.report_file_path = ""
            except Exception as e:
                st.error(f"An unexpected error occurred during report generation: {e}")
                st.session_state.generated_report_text = ""
                st.session_state.report_file_path = ""

# --- Display Generated Report ---
st.markdown("---")
st.header("Generated Report Preview")

if st.session_state.generated_report_text:
    st.text_area("Report Content:", st.session_state.generated_report_text, height=300)
    if st.session_state.report_file_path:
        st.markdown(f"**Report saved at:** `{st.session_state.report_file_path}`")
        # Optional: Add a download button for the generated .txt file
        with open(st.session_state.report_file_path, "r", encoding="utf-8") as file:
            st.download_button(
                label="Download Report (Text File)",
                data=file.read(),
                file_name=os.path.basename(st.session_state.report_file_path),
                mime="text/plain"
            )
else:
    st.info("Generated report will appear here.")

# --- Current Report Data (from ground_site_report.json for reference) ---
st.markdown("---")
st.header("Raw Observation Data (from ground_site_report.json)")
# Load and display data for reference, similar to the previous app
all_ground_site_data = load_all_report_data_from_json_file()
if all_ground_site_data:
    df_raw = pd.DataFrame(all_ground_site_data)
    st.dataframe(df_raw[["Timestamp", "Employee ID", "Type", "Task Group", "Original Comment"]])
else:
    st.info(f"No raw observation data found in `{REPORT_DATA_FILE}`.")

st.markdown("---")
st.markdown(f"**Note:** Ensure your Mistral AI model server is running at `{LLAMA_URL}` for report generation.")
st.markdown(f"Generated text reports will be saved in the `{OUTPUT_REPORTS_DIR}` directory.")