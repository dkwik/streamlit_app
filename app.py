import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from google.cloud import bigquery
from google.oauth2 import service_account

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)


# Function to load jobs
@st.cache_data
def load_data(query):
    df = pd.read_gbq(query, credentials=credentials)
    return df

# Initialize initial dataset
initial_query = """
SELECT 
SOC_TITLE,
EMPLOYER_NAME, 
EMPLOYER_CITY,
EMPLOYER_STATE,
COUNT(EMPLOYER_NAME) Requests_Filed
FROM `diversely-383001.lca_data.h1b_2020_2022_mvp` 
WHERE EMPLOYER_STATE IN ('MI', 'IL', 'WI')
AND PW_WAGE_LEVEL = 'I'
GROUP BY SOC_TITLE, EMPLOYER_NAME, EMPLOYER_CITY, EMPLOYER_STATE"""
df = load_data(initial_query)

def main():
    menu = ["Home"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    st.title("International Job Board")
    
    if choice == "Home":
        st.subheader("Search for jobs that have the highest likelihood of sponsoring you")

        # Search Form
        with st.form(key='job_search_form'):
            relocate_question = st.multiselect('How far are you willing to relocate out of Grand Rapids?',
                                               ('Grand Rapids only',
                                                'Surrounding cities (e.g Wyoming, Holland, Grand Haven, Walker, Grandville, etc.)', 
                                                'Major cities slightly further from Grand Rapids (e.g Detroit, Chicago, Milwaukee, Fort Wayne, Cleveland, etc.)'))

            plans_question = st.multiselect('What are your long term plans for staying in the US?', 
                                          ('I want to stay in the US longer term (I need a H-1B sponsorship)',
                                          'I want to stay in the US just for the short term (I just want to use my OPT)'))
            
            startdate_question = st.multiselect('How urgent is your job search?',
                                                ("Extremely urgent - I'm on my 90 Day OPT Clock",
                                                 "Somewhat urgent - I'm approaching graduation and am actively looking for jobs",
                                                 "Not Urgent - I have time to be strategic about networking"))
            
            
            submit_button = st.form_submit_button(label='Submit')
            
        
        st.subheader("Select preferences for jobs search")
        # Job variables
        job_var1, job_var2, job_var3 = st.columns(3)
        with job_var1:
            job_select_options = df['SOC_TITLE'].unique()
            job_select = st.multiselect(label= "Select job type(s)", options = job_select_options)
        with job_var2:
            state_select_options = df[df['SOC_TITLE'].isin(job_select)]["EMPLOYER_STATE"].unique()
            state_select = st.multiselect(label = "Select state(s)", options = state_select_options)
        with job_var3:
            city_select_options = df[df["EMPLOYER_STATE"].isin(state_select)]['EMPLOYER_CITY'].unique()
            city_select = st.multiselect(label = "Select city(s)", options = city_select_options)

            
        # Output dataframe
        df_output= df.loc[(df['SOC_TITLE'].isin(job_select)) 
                            & (df['EMPLOYER_STATE'].isin(state_select)) 
                            & (df['EMPLOYER_CITY'].isin(city_select))]
        # Change employer list based on conditions
        st.dataframe(df_output)
    

        # CONTACT FORM
        st.subheader("Help us learn how to contact you for more opportunities")
        
        with st.form(key='form1'):
            firstname = st.text_input("First Name")
            lastname = st.text_input("Last Name")
            email = st.text_input("Email")
            mobile = st.text_input("Mobile")
            best_friend = st.text_input("best friend")
            
            submit_button = st.form_submit_button(label = "Search")
            

        
if __name__ == '__main__':
    main()