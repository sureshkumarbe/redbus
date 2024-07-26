import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import db_service as dbservice
import time

def scrap_data(state_transport, state_transport_link):
    #Global Variables
    list_pages = []

    # Setting up the web driver
    driver = webdriver.Chrome()

    # To get all the bus links
    go_to_route(driver, state_transport_link)    
    
    # Wait for page to load
    time.sleep(5)

    # To maximize the window
    driver.maximize_window()

    # To scroll the page by 1500px vertically down
    driver.execute_script("window.scrollBy(0, 1500);", "")

    # To get number of pages and store in list_pages
    page_element = driver.find_element(By.XPATH,"//div[@class='DC_117_paginationTable']")     
    list_pages.append(page_element.text)
    list_pages = list_pages[0].split('\n')    

    # To get last page number    
    last_page = int(list_pages[-1])

    # To start webscrapping and scrap data for each pages
    for i in range(1, last_page+1):
        print(str(i))
        if(i > 1):
            # Function to go to route
            go_to_route(driver, state_transport_link)

            # Pause the program for 5 seconds
            time.sleep(5)
            
            page_navigation(str(i), driver)

            # Pause the program for 5 seconds
            time.sleep(5)
            
            # Function to Start Web Scrapping
            start_webscrapping(state_transport, driver)
        else:
            # Function to Start Web Scrapping
            start_webscrapping(state_transport, driver)
    
    # To close the web driver
    driver.close()
    
    return

# Function to Start Web Scrapping
def start_webscrapping(state_transport, driver):
    # Pause the program for 5 seconds  
    time.sleep(5)

    # Function to get all bus routes in the state transport
    route_buses = get_bus_route(driver)                
    
    for route_bus in route_buses:
        active_bus_route = route_bus['route']
        active_bus_routelink = route_bus['routelink']
        driver.get(active_bus_routelink)
        
        # Pause the program for 5 seconds
        time.sleep(5)

        # Function to scroll the page down
        if(scroll_down(driver)):
            # Function to Click on View Buses Button
            if(click_view_page(driver)):
                # Function to extract bus details
                list_bus_data = extract_bus_details(state_transport, active_bus_route, active_bus_routelink, driver)

                # Convert list to dataframe
                df_bus_data = pd.DataFrame(list_bus_data)

                # Insert data into redbus MySQL database
                dbservice.insert_data(df_bus_data)

                # Back to previous page
                driver.back()
            else:
                # Back to previous page
                driver.back()
        else:
            # Back to previous page
            driver.back()
    return

# Function to go to route
def go_to_route(driver, state_transport_link):
    return driver.get(state_transport_link)

# Function to get all bus routes in the state transport
def get_bus_route(driver):
    list_route_buses = []
    route_buses = driver.find_elements(By.CSS_SELECTOR,"a[class='route']")
    for route_bus in route_buses:
        list_route_buses.append({"route": route_bus.text, "routelink": route_bus.get_attribute('href')})
    return list_route_buses

# Function to Scroll Page Down
def scroll_down(driver):
    # Get scroll height.
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Pause the program execution for 2 seconds
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            return True

        last_height = new_height

# Function to Click on View Buses Button
def click_view_page(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollTop);")
    time.sleep(2)

    try:
        buttons = driver.find_elements(By.XPATH, "//div[@class='button' and text()='View Buses']")
        for m in range(0,len(buttons)):
            driver.execute_script("arguments[0].scrollIntoView(true);", buttons[m])
            driver.execute_script("arguments[0].click()", buttons[m])
        driver.execute_script("window.scrollTo(0, document.body.scrollTop);")
    except:
        print("No View Buses Button Found")
    return True


# Function to Extract Bus Details
def extract_bus_details(state_transport, bus_route, bus_link, driver):
    bus_data_arr = []
    busesdiv = driver.find_elements(By.XPATH,"//div[@class='clearfix row-one']")

    for bus in busesdiv:
        
        try:
            busname = bus.find_element(By.XPATH,".//div[@class='column-two p-right-10 w-30 fl']//div[@class='travels lh-24 f-bold d-color']").text
        except NoSuchElementException:
            busname = ""
        
        try:
            bustype = bus.find_element(By.XPATH,".//div[@class='column-two p-right-10 w-30 fl']//div[@class='bus-type f-12 m-top-16 l-color evBus']").text
        except NoSuchElementException:
            bustype = ""
        

        try:
            busdeparturetime = bus.find_element(By.XPATH,".//div[@class='column-three p-right-10 w-10 fl']//div[@class='dp-time f-19 d-color f-bold']").text
        except NoSuchElementException:
            busdeparturetime = ""                

        try:
            busduration = bus.find_element(By.XPATH,".//div[@class='column-four p-right-10 w-10 fl']//div[@class='dur l-color lh-24']").text
        except NoSuchElementException:
            busduration = ""
        

        try:
            busarraivaltime = bus.find_element(By.XPATH,".//div[@class='column-five p-right-10 w-10 fl']//div[@class='bp-time f-19 d-color disp-Inline']").text
        except NoSuchElementException:
            busarraivaltime = ""
        

        try:
            busrating = bus.find_element(By.XPATH,".//div[@class='column-six p-right-10 w-10 fl']//div[@class='rating-sec lh-24']").text
        except NoSuchElementException:
            busrating = 0.0
    
        try:
            busprice = bus.find_element(By.XPATH,".//div[@class='column-seven p-right-10 w-15 fl']//div[@class='seat-fare ']//div[@class='fare d-block']//span[@class='f-19 f-bold' or @class='f-bold f-19']").text
        except NoSuchElementException:
            busprice = "0"
        
        try:
            busseats = bus.find_element(By.XPATH,".//div[@class='column-eight w-15 fl']").text
        except NoSuchElementException:
            busseats = ""

        if busseats == "":
            busseats = 0
            busseattype = ""
        else:    
            if "\n" in busseats:
                try:
                    busseatsplit = busseats.split("\n")

                    #Seats Available
                    seatsavailable = busseatsplit[0]

                    try:
                        seatsavailablesplit = seatsavailable.split(" ")

                        busseats = int(seatsavailablesplit[0])
                    except:
                        busseats = 0
                    
                    #Seat Type
                    busseattype = busseatsplit[1]
                except:
                    busseatsplit = busseats

                    try:
                        seatsavailablesplit = seatsavailable.split(" ")

                        busseats = int(seatsavailablesplit[0])
                    except:
                        busseats = 0

                    #Seat Type
                    busseattype = ""            
            else:
                #Seats Available
                seatsavailable = busseats
                try:
                    seatsavailablesplit = seatsavailable.split(" ")

                    busseats = int(seatsavailablesplit[0])
                except:
                    busseats = 0
                                
                #Seat Type
                busseattype = ""

        
        #print(busname, bustype, busdeparturetime, busduration, busarraivaltime, busrating, busprice, busseats, busseattype)

        bus_data = dict(
            state_transport_name = state_transport,
            route_name = bus_route,
            route_link = bus_link,
            bus_name = busname,
            bus_type = bustype,
            departing_time = busdeparturetime, 
            duration = busduration,
            arrival_time = busarraivaltime,  
            star_rating = float(busrating),
            fare_price = busprice,
            seats_available = busseats,
            seat_type = busseattype
        )

        bus_data_arr.append(bus_data)
    
    return bus_data_arr

# Funtion to Navigating Page
def page_navigation(page_number, driver):
    driver.execute_script("window.scrollBy(0, 1500);", "")
    time.sleep(5)
    active_page = driver.find_element(By.XPATH,f"//div[@class='DC_117_pageTabs ' and text()='{page_number}']")            
    active_page.click()


