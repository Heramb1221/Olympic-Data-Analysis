import streamlit as st
import pandas as pd
import zipfile
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
import preprocessor, helper
import os

# --- Load Data from Local GZ File ---
def load_data_from_repo(gz_path):
    if gz_path.endswith('.gz'):
        df = pd.read_csv(gz_path, compression='gzip')
    else:
        raise ValueError("Unsupported file type. Expected a .gz file.")
    return df

# --- Data Loading ---
# Local path of the GZ file
GZ_FILE_PATH = 'athlete_events.gz'  # Make sure this is the exact name and path
df = load_data_from_repo(GZ_FILE_PATH)

region_df = pd.read_csv('noc_regions.csv')  # This remains unchanged

region_df = pd.read_csv('noc_regions.csv')

# --- Preprocessing ---
df = preprocessor.preprocess(df, region_df)

# --- Sidebar ---
st.sidebar.title('Olympics Analysis')

user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis')
)

# --- Medal Tally ---
if user_menu == 'Medal Tally':
    st.sidebar.header('Medal Tally')
    years, country = helper.country_year_list(df)
    selected_year = st.sidebar.selectbox('Select Year', years)
    selected_country = st.sidebar.selectbox('Select Country', country)
    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    if selected_country == 'Overall' and selected_year == 'Overall':
        st.title('Overall Tally')
    if selected_country == 'Overall' and selected_year != 'Overall':
        st.title('Medal tally in ' + str(selected_year) + ' Olympics')
    if selected_country != 'Overall' and selected_year == 'Overall':
        st.title(selected_country + ' overall performance')
    if selected_country != "Overall" and selected_year != 'Overall':
        st.title(selected_country + " performance in " + str(selected_year) + ' Olympics')

    st.table(medal_tally)

# --- Overall Analysis ---
if user_menu == 'Overall Analysis':
    editions = df['Year'].nunique() - 1
    cities = df['City'].nunique()
    sports = df['Sport'].nunique()
    events = df['Event'].nunique()
    athletes = df['Name'].nunique()
    nations = df['region'].nunique()

    st.title("Top Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)

    # Visualizations
    nations_over_time = helper.data_over_time(df, 'region')
    fig = px.line(nations_over_time, x='Edition', y='region', markers=True, title='Participating nations over the years')
    fig.update_layout(xaxis_title='Olympic Year', yaxis_title='Number of Countries')
    st.plotly_chart(fig)

    events_over_time = helper.data_over_time(df, 'Event')
    fig = px.line(events_over_time, x='Edition', y='Event', markers=True, title='Events over the years')
    fig.update_layout(xaxis_title='Olympic Year', yaxis_title='Number of Events')
    st.plotly_chart(fig)

    athlete_over_time = helper.data_over_time(df, 'Name')
    fig = px.line(athlete_over_time, x='Edition', y='Name', markers=True, title='Athletes over the years')
    fig.update_layout(xaxis_title='Olympic Year', yaxis_title='Number of Athletes')
    st.plotly_chart(fig)

    st.title('No. of Events over time (Every Sport)')
    fig, ax = plt.subplots(figsize=(20, 20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    ax = sns.heatmap(x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype(int), annot=True)
    st.pyplot(fig)

# --- Country-wise Analysis ---
if user_menu == 'Country-wise Analysis':
    st.sidebar.title('Country-wise Analysis')
    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()
    selected_country = st.sidebar.selectbox('Select a country', country_list)

    country_df = helper.yearwise_medal_tally(df, selected_country)
    fig = px.line(country_df, x='Year', y='Medal')
    st.title(selected_country + ' Medal Tally over the years')
    st.plotly_chart(fig)

    st.title(selected_country + ' excels in the following sports')
    pt = helper.country_event_heatmap(df, selected_country)
    fig, ax = plt.subplots(figsize=(20, 20))
    ax = sns.heatmap(pt, annot=True)
    st.pyplot(fig)

    top10_df = helper.most_successful_countrywise(df, selected_country)
    st.title('Top 10 athletes of ' + selected_country)
    st.table(top10_df)

# --- Athlete-wise Analysis ---
if user_menu == 'Athlete-wise Analysis':
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    athlete_df['MedalType'] = athlete_df['Medal'].fillna('No Medal')

    fig = px.histogram(athlete_df, x='Age', color='MedalType', nbins=50, title='Age Distribution by Medal Type',
                       labels={'Age': 'Athlete Age', 'MedalType': 'Medal'}, opacity=0.7)
    fig.update_layout(bargap=0.1)
    st.title('Distribution of Age')
    st.plotly_chart(fig)

    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4],
                             ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],
                             show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age")
    st.plotly_chart(fig)

    x = []
    name = []
    famous_sports = ['Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics', 'Swimming', 'Badminton', 'Sailing',
                     'Gymnastics', 'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling', 'Water Polo', 'Hockey',
                     'Rowing', 'Fencing', 'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving', 'Canoeing', 'Tennis',
                     'Golf', 'Softball', 'Archery', 'Volleyball', 'Synchronized Swimming', 'Table Tennis', 'Baseball',
                     'Rhythmic Gymnastics', 'Rugby Sevens', 'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey']
    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age wrt Sports (Gold Medalists)")
    st.plotly_chart(fig)

    st.title('Height Vs Weight')
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox('Select a Sport', sport_list)
    temp_df = helper.weight_v_height(df, selected_sport)
    fig = px.scatter(temp_df, x='Weight', y='Height', color='Medal', hover_name='Name')
    st.plotly_chart(fig)
