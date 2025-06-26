import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout="wide")
st.title("Ground Site Work - Comments Page")

LLAMA_URL = "http://127.0.0.1:8080/completion"
REPORT_FILE = "ground_site_report.json"

# --- Helper Functions for File Operations ---

def load_report_data():
    """Loads report data from the JSON file as a single JSON array."""
    if os.path.exists(REPORT_FILE):
        try:
            with open(REPORT_FILE, 'r') as f:
                data = json.load(f) # Load the entire JSON array
                if not isinstance(data, list): # Ensure it's a list
                    st.warning(f"Warning: {REPORT_FILE} does not contain a JSON array. Initializing as empty.")
                    return []
            return data
        except json.JSONDecodeError:
            st.error(f"Error decoding JSON from {REPORT_FILE}. File might be corrupted or not a valid JSON array. Initializing as empty.")
            return []
        except Exception as e:
            st.error(f"Error reading {REPORT_FILE}: {e}")
            return []
    return [] # Return empty list if file doesn't exist

def save_all_report_data(data_to_save):
    """Saves the entire list of report data to the JSON file as a single JSON array, overwriting existing content."""
    try:
        with open(REPORT_FILE, 'w') as f: # Open in write mode ('w') to overwrite
            json.dump(data_to_save, f, indent=4) # Use indent for pretty-printing
    except Exception as e:
        st.error(f"Error writing to {REPORT_FILE}: {e}")

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
# Load existing report data at the start of the session
if "report_data" not in st.session_state:
    st.session_state.report_data = load_report_data()
if "current_classified_data" not in st.session_state:
    st.session_state.current_classified_data = None

# --- User Input Fields ---
st.header("Submit a Comment")
col_input1, col_input2 = st.columns([1, 3])
with col_input1:
    employee_id = st.text_input("Employee ID:", key="employee_id")
with col_input2:
    comment_text = st.text_area("Your Observation/Comment:", key="comment_text", height=100)

if st.button("Submit Comment for Classification"):
    if not employee_id.strip():
        st.error("Please enter an Employee ID.")
    elif not comment_text.strip():
        st.error("Please enter your Observation/Comment.")
    else:
        prompt = f"""
<|im_start|> You: You are a classification assistant.
Classify the text into JSON with two fields:
- "type": exact class label
- "task_group": relevant functional group
Only return JSON.

Input: {comment_text} <|im_end|>
<|im_start|> assistant
"""
        payload = {
            "prompt": prompt,
            "temperature": 0.5,
            "n_predict": 256,
            "stream": False,
            "stop": ["<|im_end|>"],
        }

        try:
            response = requests.post(LLAMA_URL, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            ai_raw_output = result.get("content", "").strip()

            st.session_state.chat_history.append(("You", f"Employee ID: {employee_id}\nComment: {comment_text}"))
            st.session_state.chat_history.append(("AI (Raw Output)", ai_raw_output))

            try:
                classified_data = json.loads(ai_raw_output)
                c_type = classified_data.get("type", "N/A")
                c_task_group = classified_data.get("task_group", "N/A")

                st.session_state.current_classified_data = {
                    "Employee ID": employee_id,
                    "Type": c_type,
                    "Task Group": c_task_group,
                    "Original Comment": comment_text,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success("Comment classified successfully!")

            except json.JSONDecodeError:
                st.error("Error: AI did not return a valid JSON output. Please check the model's response format.")
                st.session_state.current_classified_data = None

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to AI model: {e}. Please ensure the model server is running at {LLAMA_URL}.")
            st.session_state.current_classified_data = None
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.session_state.current_classified_data = None

# --- Display Classified Output to User (More Compact) ---
st.markdown("---")
st.header("Classified Comment Details")

if st.session_state.current_classified_data:
    st.info(f"""
    **Employee ID:** {st.session_state.current_classified_data["Employee ID"]}
    **Type:** {st.session_state.current_classified_data["Type"]}
    **Task Group:** {st.session_state.current_classified_data["Task Group"]}
    """)

    if st.button("Add to Report"):
        # Add to session state for immediate display
        st.session_state.report_data.append(st.session_state.current_classified_data)
        # Save the ENTIRE updated list to JSON file
        save_all_report_data(st.session_state.report_data)
        st.success("Comment added to report and saved!")
        st.session_state.current_classified_data = None
else:
    st.info("Submit a comment above to see its classified details.")

# --- Inner Working (AI Chat History for Developers) ---
st.markdown("---")
st.header("Logs for OUTPUT")
display_limit = 5
for speaker, text in st.session_state.chat_history[-display_limit:]:
    if speaker == "AI (Raw Output)":
        try:
            st.json(json.loads(text))
        except json.JSONDecodeError:
            st.code(text)
    else:
        st.markdown(f"**{speaker}:** {text}")

# --- Current Report (Displays all data from file) ---
st.markdown("---")
st.header("Current Report (from file)")

# Always load the latest data from the file before displaying
# We need to reload here because 'Add to Report' button triggers a rerun,
# but the session_state.report_data is already updated.
# This ensures consistency, especially if multiple app instances were writing.
current_report_from_file_for_display = load_report_data()

if current_report_from_file_for_display:
    df = pd.DataFrame(current_report_from_file_for_display)
    st.dataframe(df[["Timestamp", "Employee ID", "Type", "Task Group", "Original Comment"]])
    st.markdown(f"Data is persisted in `{REPORT_FILE}` as a JSON array.")
else:
    st.info("No comments in the report yet.")

# --- Footer ---
st.markdown("---")