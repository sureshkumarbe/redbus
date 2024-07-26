import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import db_service as dbservice
import web_scraping_service as web_scraping
import general_service as generalservice
import color as appcolor
import altair as alt
import pandas as pd
import time

# Global Variables
list_state_bus_names=[]
list_state_bus_links=[]

# To create redbus database in MySQL
dbservice.create_database()

# To get all the bus links from redbus.in
for item in generalservice.dict_bus_links:    
    list_state_bus_names.append(item['route'])
    list_state_bus_links.append(item['route_link'])

#print(list_state_bus_names)
#print(list_state_bus_links)

# Setting Streamlit
icon=Image.open("logo.png")
st.set_page_config(page_title='RedBus Project',
                    page_icon=icon,
                    layout='wide',
                    initial_sidebar_state='expanded')

# To remove Streamlit Menu, Delopy Button and Footer
hide_menu_style="""<style>#MainMenu {visibility:hidden;} .stDeployButton {visibility:hidden;} footer {visibility: hidden;}</style>"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

section_style="""<style>.st-emotion-cache-1jicfl2 {padding: 2rem !important;}</style>"""
st.markdown(section_style, unsafe_allow_html=True)

# Setting up streamlit sidebar menu with options
with st.sidebar:
    option_selected = option_menu("Menu",
                        ["Home","Data Collection and Storing in MySQL","Analysis using SQL", "Data Visualization"],
                        icons=["house","database", "filetype-sql", "bar-chart-line"],
                        menu_icon="menu-up",
                        default_index=0,
                        styles={
                            "container": {"font-size": "18px", "font-family": "sans-serif", "border": "1px solid white"},
                            "icon": {"color": "white", "font-size": "18px"}, 
                            "nav-link": {"color":"white","font-size": "15px", "text-align": "left", "--hover-color": "#1d232f"},
                            "nav-link-selected": {"background-color": "#d94f55"}
                            }
                        )
    
# Setting up the option "Home" in streamlit page
if option_selected == "Home":
    st.markdown(f"<p style='text-align: center; font-size: 35px; font-family: sans-serif; font-weight: bold'><span style='color: {appcolor.primaryColor};'>Red</span>Bus WebScrapping and Analysis using MySQL</p>", unsafe_allow_html=True)
    st.subheader(':blue[Overview :]')
    st.markdown('''Build a Redbus Data Scraping and Filtering with Streamlit Application 
                to extract information from Redbus, including bus routes, schedules, prices, 
                seat availability and seat type. By streamlining data collection and providing powerful 
                tools for data-driven decision-making, this project can significantly 
                improve operational efficiency and strategic planning in the transportation industry.''')
    st.subheader(':blue[Technologies Used :]')    
    st.markdown('''
                - Selenium
                - Streamlit
                - SQL
                - Python''')
    st.subheader(':blue[Skill Take Away :]')
    st.markdown('''Web Scraping using Selenium, Python Scripting, Data Management using SQL, Streamlit''')
    st.subheader(':blue[Contact :]')
    st.markdown('#### linkedin: www.linkedin.com/in/suresh-kumar-k')
    st.markdown('#### Email : sureshkumarbecbe@gmail.com')

# Setting up the option "Data Collection and Storing in MySQL" in streamlit page
if option_selected == "Data Collection and Storing in MySQL":
    st.markdown(f"<p style='text-align: center; font-size: 35px; font-family: sans-serif; font-weight: bold'><span style='color: {appcolor.primaryColor};'>Data </span>Collection and Storing in MySQL</p>", unsafe_allow_html=True)
    st.subheader(':blue[Requirement :]')
    st.markdown('''
                Web Scrap the information about bus services available on Redbus, which includes the following fields:
                - Bus Routes Name
                - Bus Routes Link
                - Bus Name
                - Bus Type (Sleeper/Seater/AC/Non-AC)
                - Departing Time
                - Duration
                - Reaching Time
                - Star Rating
                - Price
                - Seat Availability''')

    #st.subheader(':blue[State Transport Authority :]')
    

    col1, col2, col3 = st.columns([4, 4, 4], vertical_alignment="bottom")
    
    with col1:
        selectbox_option_selected = st.selectbox('Select State', list_state_bus_names)
    with col2:
        scrap_button = st.button("Scrap Data and Upload to MySQL database")
        if scrap_button: # upload the web scraped redbus data into MYSQL database
            with st.spinner('Upload in progress...'):                
                try:
                    state_transport = ''
                    state_transport_link = ''
                
                    # To create and use the bus_route table in MySQL
                    dbservice.create_table()

                    for item in generalservice.dict_bus_links:
                        if item['route'] == selectbox_option_selected:
                            state_transport = item['route']
                            state_transport_link = item['route_link']
                        else:
                            pass
                    
                    # Check the data in MySql for selected state transport
                    check_data = dbservice.check_data(selectbox_option_selected)

                    if(check_data is not None and len(check_data) > 0):
                        st.toast("Successfully deleted data from MySQL Database", icon=":material/thumb_up:")                        
                    else:
                        pass
                    
                    web_scraping.scrap_data(state_transport, state_transport_link)
                    st.toast("Data successfully uploaded to MySQL database.", icon="✅")                        
                    st.balloons()                                      

                except:
                    pass

# Setting up the option "Analysis using SQL" in streamlit page
if option_selected == "Analysis using SQL":
    st.markdown(f"<p style='text-align: center; font-size: 35px; font-family: sans-serif; font-weight: bold'><span style='color: {appcolor.primaryColor};'>Analysis </span>using SQL</p>", unsafe_allow_html=True)    
    sql_state_transport = dbservice.get_state_transports()
    option_state_transport = st.selectbox('Select State Transport', sql_state_transport)

    col1, col2, col3 = st.columns([4, 4, 4], vertical_alignment="top")

    with col1:
        sql_bus_route = dbservice.get_bus_routes(option_state_transport)
        option_bus_route = st.selectbox('Select Bus Route', sql_bus_route)

    with col2:
        sql_bus_type = dbservice.get_bus_type(option_state_transport, option_bus_route)
        option_bus_type = st.selectbox('Select Bus Type', sql_bus_type)

    with col3:
        # Create a slider for selecting the price range
        start_price, end_price = st.slider(
            "Select Price Range",
            min_value=0,
            max_value=15000,
            value=(0, 15000)
        )
    
    col4, col5, col6 = st.columns([4, 4, 4], vertical_alignment="top")
    with col4:
        # Create a slider for selecting the star rating
        start_rating, end_rating = st.slider(
            "Select Star Rating Range",
            min_value=0,
            max_value=5,
            value=(0, 5)
        )
    with col5:
        start_seat, end_seat = st.slider(
            'Select Seat Availability Range',
            min_value=1,
            max_value=80,
            value=(1, 80),
            step=1
        )
    with col6:
        pass

            
    sql_bus_data = dbservice.get_bus_data(option_state_transport, option_bus_route, option_bus_type, start_price, end_price, start_rating, end_rating, start_seat, end_seat)    
    # Check if data is returned
    if sql_bus_data is None or len(sql_bus_data) == 0:
        st.write("No Data available in Database")
    else:
        # Convert the data to a DataFrame
        st.dataframe(sql_bus_data)

# Setting up the option "Data Visualization" in streamlit page
if option_selected == "Data Visualization":
    st.markdown(f"<p style='text-align: center; font-size: 35px; font-family: sans-serif; font-weight: bold'><span style='color: {appcolor.primaryColor};'>Data </span>Visualization</p>", unsafe_allow_html=True)    
    
    # Bar Chart: Proportion of different state transports
    st.markdown(f"<p style='text-align: center; font-size: 30px; font-family: sans-serif; font-weight: bold'><span style='color: {appcolor.primaryColor};'>Bar </span>Chart</p>", unsafe_allow_html=True)    

    st.subheader(':blue[State Transports Vs Number of Buses]')

    # Load data
    sql_bus_state_data = dbservice.dv_get_state_buses()

        
    # Create a DataFrame
    df = pd.DataFrame(sql_bus_state_data)

    # Create a bar chart using Altair
    chart = alt.Chart(df).mark_bar().encode(
            x='State Transport',
            y='Number of Buses',
            color='State Transport'
            )

    st.altair_chart(chart, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    
    sql_state_transport = dbservice.dv_get_state_transports()
    option_state_transport = st.selectbox('Select State Transport', sql_state_transport)
    
    if option_state_transport is None or len(option_state_transport) == 0:
        st.write("No Data available in Database")
    else:
        # Load State Transport data
        sql_bus_data = dbservice.dv_get_data_from_mysql(option_state_transport)

        # Pie Chart: Proportion of different bus types
        st.markdown(f"<p style='text-align: center; font-size: 30px; font-family: sans-serif; font-weight: bold'><span style='color: {appcolor.primaryColor};'>Pie </span>Chart</p>", unsafe_allow_html=True)    

        st.subheader(':blue[Bus Types Vs Number of Buses]')
        
        bus_type_counts = sql_bus_data['bus_type'].value_counts().reset_index()
        bus_type_counts.columns = ['bus_type', 'count']
        pie_chart = alt.Chart(bus_type_counts).mark_arc().encode(
            theta=alt.Theta(field="count", type="quantitative", title='No. of Buses'),
            color=alt.Color(field="bus_type", type="nominal", title='Bus Type'),
            tooltip=[                
                alt.Tooltip('bus_type', title='Bus Type'), 
                alt.Tooltip('count', title='No. of Buses')
            ]            
        )
        st.altair_chart(pie_chart, use_container_width=True)

        # Scatter Plot: Correlation between fare price and star rating
        st.markdown(f"<p style='text-align: center; font-size: 30px; font-family: sans-serif; font-weight: bold'><span style='color: {appcolor.primaryColor};'>Scatter </span>Chart</p>", unsafe_allow_html=True)    

        st.subheader(':blue[Correlation between Fare Price and Star Rating]')        

        scatter_plot = alt.Chart(sql_bus_data).mark_circle().encode(
            x=alt.X('fare_price', title='Fare Price'), # Change X Axis title here
            y=alt.Y('star_rating', title='Star Rating'), # Change Y Axis title here
            color=alt.Color('bus_type', title='Bus Type'), # Change legend title here
            tooltip=[
                alt.Tooltip('route_name', title='Route Name'),
                alt.Tooltip('bus_name', title='Bus Name'),
                alt.Tooltip('bus_type', title='Bus Type'),
                alt.Tooltip('fare_price', title='Bus Price (₹)', format='.2f'),
                alt.Tooltip('star_rating', title='Start Rating', format='.2f')                                
            ]
        )
        st.altair_chart(scatter_plot, use_container_width=True)  
