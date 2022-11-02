import streamlit as st
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.font_manager as font_manager
import streamlit.components.v1 as components
import datetime
from io import StringIO 

#Set web page to wide layout 
st.set_page_config(layout="wide",initial_sidebar_state="expanded")
st.set_option('deprecation.showPyplotGlobalUse', False)

#Setting font for all text to Raleway
st.write("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@700&display=swap');
    html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True) 


st.image("manabie_logo_original.png")
st.markdown(" ")
st.markdown(" ")
st.markdown(" ")
st.markdown(" ")
squad = st.selectbox(
    'Squad Name',
    ('Architecture', 'Authentication', 'Calendar', 
    'Entry and Exit', 'Hermes', 'Invoice', 'Learning Materials', 'Lesson Management',
    'Notification', 'Order Management', 'Study Plan', 
    'Timesheet and Expense', 'User Management', 'Virtual Classroom'))
sprint_number = st.text_input("Sprint Number: ")
start_date = st.date_input("Start Sprint Date: ") 
start_time = st.time_input("Start Sprint time (GMT+8): ")
end_date = st.date_input("End Sprint date: ")
end_time = st.time_input("End Sprint time (GMT+8): ")
uploaded_file = st.file_uploader("Sprint File: ")

if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

    # To read file as string:
    string_data = stringio.read()

    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_csv(uploaded_file)

    #Convert resolved, created and transition.date to datetime 
    dataframe["transition.date"] = pd.to_datetime(dataframe["transition.date"], format='%Y-%m-%d %H:%M:%S' ).dt.tz_localize(None) + pd.DateOffset(hours=8)
    dataframe["Resolved"] = pd.to_datetime(dataframe["Resolved"],format='%d/%m/%Y %H:%M:%S')
    dataframe["Created"] = pd.to_datetime(dataframe["Created"], format='%d/%m/%Y %H:%M:%S')
    
    #Set issue type
    issue_type = ["Bug", "Non-functional", "QA", "Task", "Epic", "Story", "Design"]

    filter_data = []
    updated_dates = []
    #Get the acknowledged date only 
    for key in dataframe['Key'].unique():
        date = dataframe.loc[dataframe['Key'] == key, 'transition.date'].min()
        filter_data.append(date)
        updated_date = dataframe.loc[dataframe['Key'] == key, 'transition.date'].max()
        updated_dates.append(updated_date)
    
    #Remove other issue type not in issue_type
    final_data = dataframe.loc[(dataframe['transition.date'].isin(filter_data))]
    final_data.loc[:,"Updated Date"] = updated_dates

    final_data =  final_data.loc[(dataframe['Issue Type'].isin(issue_type))]
    
    #Rename the columns
    final_data.rename(columns = {'Issue Type':'Issue Type', 
                            'Key':'Issue key',
                            'Issue ID':'Issue id',
                            'Assignee.displayName':'Assignee',
                            'Assignee.accountId':'Assignee Id',
                            'Story Points':'Story Points',
                            'Summary':'Summary',
                            'Status':'Closed/Not',
                            'Resolved':'Resolved',
                            'Created':'Created',
                            'transition.date':'Acknowledged'}, 
                inplace = True)

    #Conditions for "Status" column
    
    conditions = conditions = [
    (final_data["Closed/Not"]=="Closed") & (final_data["Resolved"] >= datetime.datetime.combine(end_date, end_time)),
    (final_data["Closed/Not"]=="Closed")  & (final_data["Updated Date"] <= datetime.datetime.combine(start_date, start_time)) & (final_data["Resolved"] <= datetime.datetime.combine(start_date, start_time)),
    (final_data["Closed/Not"]=="Closed")  & (final_data["Updated Date"] <= datetime.datetime.combine(start_date, start_time)) & (final_data["Resolved"].isna()),
    (final_data["Closed/Not"]=="Closed") & (final_data["Updated Date"] >= datetime.datetime.combine(end_date, end_time)),
    (final_data["Closed/Not"]=="Closed") & ((final_data["Updated Date"]>=datetime.datetime.combine(start_date, start_time)) | (final_data["Resolved"] >= datetime.datetime.combine(start_date, start_time))),
    (final_data["Closed/Not"]=="Done")  & (final_data["Updated Date"] <= datetime.datetime.combine(end_date, end_time)),
    (final_data["Closed/Not"]!="Done") | (final_data["Closed/Not"]!="Closed") 
    ]


    choices = ["Not Completed", "Completed outside of sprint","Completed outside of sprint", "Not Completed", "Completed", "Completed", "Not Completed"]
    
    #Create Sprint# column
    final_data["Sprint #"] = sprint_number
    
    #Create Duration(hours) column
    final_data["Duration(hours)"] = (final_data["Resolved"] - final_data["Acknowledged"]).astype("timedelta64[h]")
    
    final_data['Status'] = np.select(conditions, choices, default="Not Completed")
    final_data['Assignee'] = final_data['Assignee'].fillna('Unassigned')
    final_data['Story Points'] = final_data['Story Points'].fillna(0)  
    
    final_data = final_data[(final_data['Status'] == "Not Completed") |(final_data['Status'] == "Completed")]
    final_data = final_data.drop(["Updated Date"], axis = 1)
    
    #final_data.to_csv(squad + " Sprint "+ sprint_number +".csv", index=False)
    st.dataframe(final_data)
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.download_button("Download Sprint Report", 
                        final_data.to_csv(index=False),
                        file_name = squad + " Sprint "+ sprint_number +".csv",
                        mime='text/csv')
    

#st.download_button("Download Sprint Report:", final_data.to_csv(squad + " Sprint "+ sprint_number +".csv", index=False), mime='text/csv')


