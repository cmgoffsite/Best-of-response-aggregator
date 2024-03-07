import streamlit as st
import pandas as pd
import base64
from io import BytesIO

def convert_to_csv_url(sheet_url):
    # Extract the unique part of the Google Sheets URL (between 'd/' and '/edit')
    start = sheet_url.find('/d/') + 3
    end = sheet_url.find('/edit', start)
    unique_id = sheet_url[start:end]
    # Construct the CSV export URL
    csv_url = f"https://docs.google.com/spreadsheets/d/{unique_id}/export?format=csv"
    return csv_url

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

# Function to display the app logo with conditional color inversion
def display_logo():
    file_path = 'Best of Logo.png'
    with open(file_path, "rb") as file:
        logo_base64 = base64.b64encode(file.read()).decode()
    
    st.markdown(
    f"<img src='data:image/png;base64,{logo_base64}' style='height: 100px;' alt='App Logo'>", 
    unsafe_allow_html=True
)

#change favicon & site name
st.set_page_config(page_title="Best of Response Aggregator", page_icon="lm-circle-logo.ico", layout="wide")

# Streamlit GUI
def main():
    # Custom CSS for logo and selected movie
    st.markdown("""
        <style>
        .app-logo {
            height: 100px; 
            filter: invert(var(--logo-invert));
        }
        </style>
        """, unsafe_allow_html=True)
    
    display_logo()
    
    st.title("Best Of Response Aggregator")

    source_option = st.selectbox("Select data source", ["Upload CSV", "Google Sheets URL"])

    if source_option == "Upload CSV":
        uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file, dtype=str)
            process_data(df)

    elif source_option == "Google Sheets URL":
        sheet_url = st.text_input("Enter the Google Sheets URL")
        if st.button("Load Sheet"):
            csv_url = convert_to_csv_url(sheet_url)
            try:
                df = pd.read_csv(csv_url)
                st.success("Data loaded successfully!")
                process_data(df)
            except Exception as e:
                st.error(f"Error loading data: {e}")

def process_data(df):
    df['End Date'] = pd.to_datetime(df['End Date'], errors='coerce')
    df = df.sort_values(by=['Email Address', 'End Date'])
    aggregated_df = df.groupby('Email Address', as_index=False).apply(aggregate_responses)
    final_df = aggregated_df.drop_duplicates(subset=['Email Address'], keep='last')
    final_df = final_df.sort_values(by='Email Address')
    final_df = final_df.infer_objects()  # Address FutureWarning by ensuring proper dtypes
    
    # Save the cleaned, aggregated DataFrame to a new CSV file and provide for download
    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='cleaned_data.csv',
        mime='text/csv',
    )
    excel_file = to_excel(final_df)
    st.download_button(
        label="Download data as Excel",
        data=excel_file,
        file_name="cleaned_data.xlsx",
        mime="application/vnd.ms-excel"
    )

def aggregate_responses(group):
    agg_row = group.ffill().iloc[-1]
    return agg_row

if __name__ == "__main__":
    main()
