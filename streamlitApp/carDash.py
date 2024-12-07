# Streamlit web interface for visualizing car performance data. 
# For Databases for Datascience group 3 final project. 
# 

# import libs, ensure to grab dependancies from reqs file. 
import couchdb
import streamlit as st
import pandas as pd
import plotly.express as px

# environment variables for git 
import os 
from dotenv import load_dotenv

# load them in
load_dotenv()

# set them
DB_URI = os.getenv('db_url')
DB_USER = os.getenv('user')
DB_PASS = os.getenv('password')
ACTIVE_DB = os.getenv('db')

# make a connection to couch db
# args : username, password - Strings
# username and password used for db connection
def _db_connection(serverurl, username, password):
	try:
		couch = couchdb.Server(serverurl)
		couch.resource.credentials = (username, password)
		return couch
	except Error as e:
		print(f"Issue connecting to couchDB : {e}")
		return e

# fetch data from the connected couch db
# args : couch - couchDB server object, dbname - String name of database you want to access	
def _fetch_data(couch, dbname):
	try:
		if dbname in couch:
			db = couch[dbname]
			data = [doc['doc'] for doc in db.view('_all_docs', include_docs=True)]
			df = pd.DataFrame(data)
			df = df.drop(columns=['_id', '_rev', 'views'], errors='ignore')
			columns = ['make', 'model'] + [col for col in df.columns if col not in ['make', 'model']]
			df = df[columns]
			return df
		else:
			return pd.DataFrame()
	except Error as e:
		print(f"Issue retrieving data from couch, {e}")
		return pd.DataFrame()

# TODO : conquer the streamlit wall, make main pretty again
# probably maybe make little functions for everything 
def main():
    st.set_page_config(layout="wide", page_title="Cars n' Couches",  menu_items=None)
    
    # side bar configuration    
    st.sidebar.title("Group 3 - Car Data") # give it a title 
    page = st.sidebar.radio("Main Options", ["Home", "Main Analysis", "Further Insights"]) # radio menu with a sub title 

    # db connection info, hidden in an env file
    server_url = DB_URI
    username = DB_USER
    password = DB_PASS
    db_name = ACTIVE_DB

    try: # attempt a server connection
        couch = _db_connection(server_url, username, password) # connect to the couch db
        data = _fetch_data(couch, db_name) # attempt to fetch data from the couch db 

        if page == "Home": # home page selected on radio menu
            
            # Title, page information 
            st.title("Vehicle Performance Insight Dash")

            st.write("""Powered by Streamlit and CouchDB, this dashboard provides a high level overview of vehicle performance data from Kaggle.
                    Each page focuses on a different set of questions or insights. The landing page here focuses on initial discovery
                    and building familiarity with the dataset.""")

            col1, col2 = st.columns(2)

            with col1:
                unique_models = data['model'].nunique()
                st.metric("Unique Models", unique_models)
                
            with col2:
                unique_makes = data['make'].nunique()
                st.metric("Unique Makes", unique_makes)
            
            st.divider()
            if not data.empty: # if the data fetched 
                st.subheader("Table Overview:") # display the data in table form, for a quick overview of all of it 
            
                st.write("Interactive overview of entire dataset. Interactive table allows for sorting of columns.")
                st.dataframe(data, hide_index=True, width=1200)
                
                st.divider() # lots of these, they look nice. 
                
                # interactive plot, allowing user to compare any two variables from the data set and plot it 
                st.subheader("Value Comparison")
                st.write("Interactive comparison of two metrics. Select X and Y axis to plot. Use the radio menu to select visualization type.")
                
                columns = list(data.columns)
                xVal = st.selectbox("Select metric for X axis", columns)
                yVal = st.selectbox("Select metric for Y axis", columns)

                chart_type = st.radio(
                    "Select the type of chart to display:",
                    ("Bar Chart", "Scatterplot"), horizontal=True
                )

                if xVal and yVal: # plot once they've provided values, or use the defaults if those are still set (who knows where they may go)
                    if chart_type == "Bar Chart":
                        plot = px.bar(data, x=xVal, y=yVal, title=f"Plot of ({xVal}, {yVal})")
                    else: # lazy yes, but it works. Only two graph options displaying here 
                        plot = px.scatter(data, x=xVal, y=yVal, title=f"Plot of ({xVal}, {yVal})")
                    st.plotly_chart(plot)
                else:
                    st.warning("No data found or database does not exist.")
                    
                st.divider()

        elif page == "Further Insights": # key insights (page 2 ) selected on radio menu 
            st.title("Key Insights")
            
            if not data.empty: # if we got data from the fetch 

                if 'model' in data.columns and 'make' in data.columns:
                    # Get the top 5 most frequent models and their counts
                    model_counts = data['model'].value_counts().head(10)
                    top_models = model_counts.index
                
                    # Filter the dataset to get the make for these models
                    top_model_makes = data[data['model'].isin(top_models)][['make', 'model']]
                    top_model_makes = top_model_makes.drop_duplicates()  # Ensure uniqueness of make-model pairs
                
                    # Combine the counts with make and model for display
                    result = pd.DataFrame({
                        'Model': top_models,
                        'Count': model_counts.values
                    }).merge(top_model_makes, left_on='Model', right_on='model', how='left')
                
                    # Display the result in a more visual way
                    fig = px.bar(
                        result,
                        x='Model',
                        y='Count',
                        color='make',
                        title="10  Most Frequent Models with Their Makes",
                        labels={'Count': 'Frequency', 'make': 'Make'}
                    )
                    st.plotly_chart(fig)
                
                st.divider()

                if 'make' in data.columns:
                    # Get the top 5 most frequent makes and their counts
                    make_counts = data['make'].value_counts().head(10).reset_index()
                    make_counts.columns = ['Make', 'Count']  # Rename columns for clarity
                
                    # Create a customized bar chart
                    fig = px.bar(
                        make_counts,
                        x='Make',
                        y='Count',
                        color='Make',  # Use color to differentiate makes
                        title="Manufactuers with most individual makes",
                        labels={'Count': 'Frequency', 'Make': 'Car Make'},
                        text='Count'  # Add count labels on bars
                    )
                
                    # Update chart appearance
                    fig.update_layout(
                        xaxis_title="Car Make",
                        yaxis_title="Frequency",
                        showlegend=False  # Disable legend since make names are on x-axis
                    )
                    fig.update_traces(textposition='outside')  # Position labels outside the bars
                
                    # Display the chart
                    st.plotly_chart(fig)
                
                st.divider()
                
                # Calculate averages for mpg metrics
                combination_avg = data['combination_mpg'].mean() if 'combination_mpg' in data.columns else None
                city_avg = data['city_mpg'].mean() if 'city_mpg' in data.columns else None
                highway_avg = data['highway_mpg'].mean() if 'highway_mpg' in data.columns else None
                
                col1, col2, col3 = st.columns(3) # make columns for formatting 
                
                # if averages were created correctly, display them in the columns 
                if combination_avg is not None:
                    col1.metric("Avg Combination MPG", f"{combination_avg:.2f}")
                else:
                    col1.warning("Combination MPG not available")
                if city_avg is not None:
                    col2.metric("Avg City MPG", f"{city_avg:.2f}")
                else:
                    col2.warning("City MPG not available")
                if highway_avg is not None:
                    col3.metric("Avg Highway MPG", f"{highway_avg:.2f}")
                else:
                    col3.warning("Highway MPG not available")
                    
                st.divider()
                
                # displays for cars that standout for various key metrics 
                
                st.subheader("10 Best Combined Mileage Cars:") # best in combined MPG
                if 'combination_mpg' in data.columns:
                    top_cars = data[['make', 'model', 'cylinders', 'combination_mpg']].sort_values(by='combination_mpg', ascending=False).head(10)

                    st.write("These are the cars with the highest fuel efficiency across both measures.")

                    st.table(top_cars)
                else:
                    st.warning("The dataset does not include gas mileage (mpg) information.")
                    
                st.subheader("10 Best City Mileage Cars:") # best in city mileage
                if 'city_mpg' in data.columns:
                    top_cars = data[['make', 'model', 'cylinders', 'city_mpg']].sort_values(by='city_mpg', ascending=False).head(10)

                    st.write("These are the cars with the highest fuel efficienc in city scenarios.")

                    st.table(top_cars)
                else:
                    st.warning("The dataset does not include gas mileage (mpg) information.")
                    
                st.subheader("10 Best Highway Mileage Cars:") # best highway mileage 
                if 'highway_mpg' in data.columns:
                    top_cars = data[['make', 'model', 'cylinders', 'highway_mpg']].sort_values(by='highway_mpg', ascending=False).head(10)

                    st.write("These are the cars with the highest fuel efficiency in highway conditions.")

                    st.divider()

                    st.table(top_cars)
                else:
                    st.warning("The dataset does not include gas mileage (mpg) information.")
            else: 
                st.warning('no data')
                
        elif page == "Main Analysis":
            st.subheader("Do newer vehicles generally have better gas mileage?")
            
            if 'year' in data.columns and 'combination_mpg' in data.columns: # check years and mpg
                avg_by_year = data.groupby('year')['combination_mpg'].mean().reset_index() # get average 
                st.line_chart(avg_by_year.set_index('year')) # plot it

                st.write("""Here we see how the average combination MPG has trended over the years. 
                        If it doesn't show a clear upward trend, it suggests that newer vehicles 
                        may not always have better mileage. External factors like engine design, 
                         vehicle weight, and aerodynamics can be more significant.""") # descriptor 
                         
            # same general shape of question, graph / figure, write up on this page 
            
            st.divider()
            
            st.subheader("What kinds of engines get the best fuel economy?")

            if 'combination_mpg' in data.columns and 'cylinders' in data.columns and 'displacement' in data.columns:
                st.write("""Generally, smaller displacement engines and fewer cylinders tend to yield better fuel economy. 
                        Below is a scatter plot of displacement vs. combination MPG.""")
                st.vega_lite_chart(data, {
                    "width": 1280, # plot dimensions
                    "height": 500,
                    'mark': 'point', # shape of markers on the plot 
                    'encoding': {
                        'x': {'field': 'displacement', 'type': 'quantitative'}, # qualities of chart 
                        'y': {'field': 'combination_mpg', 'type': 'quantitative'},
                        'color': {'field': 'cylinders', 'type': 'quantitative'},
                    }
                })

            st.divider()
            
            st.subheader("Which manufacturers offer the most high fuel economy vehicles?")

            if 'make' in data.columns and 'combination_mpg' in data.columns:

                top_makes = (data.groupby('make')['combination_mpg'].mean() .reset_index()
                    .sort_values(by='combination_mpg', ascending=False).head(10))

                st.write("Top 10 manufacturers by average combination MPG:")
                st.table(top_makes)

            st.divider()
            
            st.subheader("Do certain manufacturers have larger presences in these markets and has this changed year-to-year?")

            if 'year' in data.columns and 'make' in data.columns:

                # Count number of models per make over the years
                models_by_year = data.groupby(['year', 'make'])['model'].nunique().reset_index()
                st.write("""Below is a line chart showing the number of unique models offered by top 
                        high-economy manufacturers over time. This can indicate market presence changes.""")

                filtered_makes = top_makes['make'].unique()
                filtered_data = models_by_year[models_by_year['make'].isin(filtered_makes)]

                # Pivot for easier charting
                pivoted = filtered_data.pivot(index='year', columns='make', values='model').fillna(0)
                st.line_chart(pivoted)
                
            st.divider()
            
            st.subheader("Does drivetrain configuration have a large impact on fuel economy?")
            if 'drive' in data.columns and 'combination_mpg' in data.columns:
                avg_by_drivetrain = data.groupby('drive')['combination_mpg'].mean().reset_index()
                st.bar_chart(avg_by_drivetrain.set_index('drive'))
                st.write("This chart shows the average combination MPG by drivetrain type (e.g., FWD, RWD, AWD).")

            st.divider()
            
            st.subheader("Do electric vehicles generally get better city or highway mileage?")

            # check for fuel type and mpgs, then check fuel type for electric cars. 
            if 'fuel_type' in data.columns and 'city_mpg' in data.columns and 'highway_mpg' in data.columns:
                ev_data = data[data['fuel_type'].str.contains('Electric', case=False, na=False)]
                
                if not ev_data.empty:
                    avg_city = ev_data['city_mpg'].mean()
                    avg_highway = ev_data['highway_mpg'].mean()
                    
                    st.write(f"Average City MPG (EVs): {avg_city:.2f}")
                    st.write(f"Average Highway MPG (EVs): {avg_highway:.2f}")
                    
                    st.write("""EVs often excel in city driving due to regenerative braking and efficient low-speed operation, 
                                 whereas internal combustion engines often have their best fuel economy at steady highway speeds. 
                                 This can lead to EVs having relatively better city mileage compared to their highway mileage 
                                 in MPGe terms.""")

                
                
            else:
                st.warning("No data found or database does not exist.") # no data :(
                
    except Exception as e: # something bad happened so error time 
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
