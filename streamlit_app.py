import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime, timedelta

# Function to initialize SQLite database and create the table if it doesn't exist
def init_db():
    conn = sqlite3.connect('wait_times.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wait_times (
        id INTEGER PRIMARY KEY,
        time INTEGER,
        submitted_at TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Function to insert a new wait time into the database
def insert_wait_time(time):
    conn = sqlite3.connect('wait_times.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO wait_times (time, submitted_at)
    VALUES (?, ?)
    ''', (time, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

# Function to fetch wait times from the last 6 hours
def get_last_6_hours():
    conn = sqlite3.connect('wait_times.db')
    cursor = conn.cursor()
    cutoff_time = (datetime.now() - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
    SELECT time, submitted_at FROM wait_times
    WHERE submitted_at > ?
    ORDER BY submitted_at
    ''', (cutoff_time,))
    rows = cursor.fetchall()
    conn.close()
    return [{"time": row[0], "submitted_at": row[1]} for row in rows]

# Apply custom CSS for green background, white text, and styled Submit button
st.markdown(
    """
    <style>
    .stApp {
        background-color: #458264; /* T&T Green Background */
    }
    h1, h2, h3, h4, h5, h6, p, div {
        color: white; /* Set title and text to white */
    }
    /* Style the Submit button */
    div.stButton > button {
        background-color: #458264 !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    div.stButton > button:hover {
        background-color: #306847 !important; /* Darker green on hover */
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize database
init_db()

# Submit wait time
st.markdown(
    """
    <h1 style="text-align: center;">
        T&T Supermarket Bellevue <br> Wait Time Estimator
    </h1>
    """,
    unsafe_allow_html=True,
)

st.header("Submit a current Wait Time")
wait_time = st.number_input("Enter wait time (minutes):", min_value=0, step=1)

if st.button("Submit"):
    insert_wait_time(wait_time)  # Save to database
    st.success("Wait time submitted successfully!")

# Fetch wait times from the last 6 hours
filtered_times = get_last_6_hours()

# Convert to a DataFrame
if filtered_times:
    df = pd.DataFrame(filtered_times)
    df['submitted_at'] = pd.to_datetime(df['submitted_at'])

    # Resample the data in 1-hour intervals and calculate average wait time
    df.set_index('submitted_at', inplace=True)
    resampled_df = df.resample('1H').mean()  # Resample by 1-hour intervals

    # Display average wait time for the last 6 hours
    avg_wait = resampled_df['time'].mean()
    st.header("Average Wait Time (Last 6 Hours)")
    st.write(f"**Average Wait Time:** {avg_wait:.2f} minutes")

    # Plot bar chart for average wait time per 1-hour interval in the last 6 hours
    st.header("Wait Times Over the Last 6 Hours (Averaged per Hour)")
    fig = px.bar(
        resampled_df,
        x=resampled_df.index,
        y='time',
        title="Average Wait Times in 1-Hour Intervals (Last 6 Hours)",
        labels={"time": "Average Wait Time (minutes)", "submitted_at": "Time"},
        color='time',
        text='time'
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("No data available for the last 6 hours.")

# Display raw data table (optional)
if st.checkbox("Show Raw Data"):
    st.write(filtered_times)
    
# Clear all data from the database
def clear_wait_times():
    conn = sqlite3.connect('wait_times.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM wait_times')  # Remove all rows
    conn.commit()
    conn.close()
if st.button("Clear All Wait Times"):
    clear_wait_times()  # Or call delete_database() if you want to delete the whole file
    st.success("All wait times have been cleared!")
