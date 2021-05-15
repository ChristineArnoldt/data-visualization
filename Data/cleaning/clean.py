import pandas as pd
import numpy as np

#read raw file with airports
airports = pd.read_csv('Data/original-kaggle-flight-data/airports.csv', sep=',', usecols=['IATA_CODE', 'AIRPORT', 'STATE' , 'LATITUDE', 'LONGITUDE'])

def run():
    #read raw file with flights
    print('reading csv')
    df = pd.read_csv('Data/original-kaggle-flight-data/flights.csv', sep=',', usecols=['YEAR', 'MONTH', 'DAY', 'DAY_OF_WEEK', 'AIRLINE', 'FLIGHT_NUMBER', 'ORIGIN_AIRPORT', 'DESTINATION_AIRPORT', 'DISTANCE', 'SCHEDULED_DEPARTURE','DEPARTURE_DELAY', 'SCHEDULED_TIME', 'ELAPSED_TIME', 'SCHEDULED_ARRIVAL', 'ARRIVAL_DELAY', 'DIVERTED', 'CANCELLED', 'CANCELLATION_REASON', 'AIR_SYSTEM_DELAY', 'SECURITY_DELAY', 'AIRLINE_DELAY', 'LATE_AIRCRAFT_DELAY', 'WEATHER_DELAY'], parse_dates=['SCHEDULED_DEPARTURE', 'SCHEDULED_ARRIVAL'])
    print(df.shape)

    #renaming columns for clarification
    df = df.rename(columns={'SCHEDULED_DEPARTURE':'SCHEDULED_DEPARTURE_LOCALTIME', 'SCHEDULED_ARRIVAL':'SCHEDULED_ARRIVAL_LOCALTIME'}).copy()

    #flitering out long distance flights (longer than 1400 miles) to reduce the size of the dataset
    print('filtering data')
    df = df[df['DISTANCE']>1400]
    print(df.shape)

    #creating datetime out of scheduled-time columns
    print('formatting datum data')
    df['SCHEDULED_DEPARTURE_LOCALTIME'] = pd.to_datetime(df['SCHEDULED_DEPARTURE_LOCALTIME'], errors='coerce', format = '%H%M')
    df['SCHEDULED_DEPARTURE_LOCALTIME'] = df['SCHEDULED_DEPARTURE_LOCALTIME'].apply(lambda dt: dt.replace(year=2015))
    df['SCHEDULED_ARRIVAL_LOCALTIME'] = pd.to_datetime(df['SCHEDULED_ARRIVAL_LOCALTIME'], errors='coerce', format = '%H%M')
    df['SCHEDULED_ARRIVAL_LOCALTIME'] = df['SCHEDULED_ARRIVAL_LOCALTIME'].apply(lambda dt: dt.replace(year=2015))

    #new column where adjustment for time difference is removed
    delta = pd.to_timedelta(df['SCHEDULED_TIME'],'minute')
    df['SCHEDULED_ARRIVAL_ORIGINTIME'] = df['SCHEDULED_DEPARTURE_LOCALTIME'] + delta
    print(df.shape)

    #merging with airports file - Please note that the merge is an outer merge so I can include all airports. In the NaN cleaning I will create a new dataframe where these rows (that do not have a flight associated with them) are removed.
    print('merging with airports.csv')
    airportflights = df.merge(airports, left_on='ORIGIN_AIRPORT', right_on='IATA_CODE', how='outer').copy().drop(columns=['ORIGIN_AIRPORT']).copy()
    airportflights = airportflights.rename(columns={'IATA_CODE':'ORIGIN_AIRPORT','AIRPORT':'ORIGIN_AIRPORT_NAME', 'CITY':'ORIGIN_CITY', 'STATE':'ORIGIN_STATE', 'LATITUDE':'ORIGIN_AIRPORT_LAT', 'LONGITUDE':'ORIGIN_AIRPORT_LON'}).copy()
    airportflights = airportflights.merge(airports, left_on='DESTINATION_AIRPORT', right_on='IATA_CODE', how='outer').drop(columns=['DESTINATION_AIRPORT']).copy()
    airportflights = airportflights.rename(columns={'IATA_CODE':'DESTINATION_AIRPORT','AIRPORT':'DESTINATION_AIRPORT_NAME', 'CITY':'DESTINATION_CITY', 'STATE':'DESTINATION_STATE', 'LATITUDE':'DESTINATION_AIRPORT_LAT', 'LONGITUDE':'DESTINATION_AIRPORT_LON'}).copy()

    #new dataframes with cancelled flights & without cancelled flights
    print('separating cancelled and non-cancelled flights')
    cancelled = airportflights[airportflights['CANCELLED'] != 0]
    nonCancelled = airportflights[airportflights['CANCELLED'] == 0]
    print('Cancelled:',cancelled.shape)
    print('nonCancelled:',nonCancelled.shape)

    #cleaning
    print('cleaning NANs')
    
    print('cleaning cancelled...')
    cancelled_withallairports_NaN = cancelled.dropna(subset=['YEAR', 'MONTH', 'DAY', 'DAY_OF_WEEK', 'FLIGHT_NUMBER', 'SCHEDULED_DEPARTURE_LOCALTIME', 'SCHEDULED_TIME', 'DISTANCE', 'SCHEDULED_ARRIVAL_LOCALTIME', 'CANCELLED', 'CANCELLATION_REASON', 'SCHEDULED_ARRIVAL_ORIGINTIME'])
    cancelled_onlyflights = cancelled.dropna(subset=['DESTINATION_AIRPORT', 'ORIGIN_AIRPORT'])
    cancelled = cancelled_withallairports_NaN.dropna(subset=['AIRLINE','ORIGIN_AIRPORT', 'DESTINATION_AIRPORT', 'ORIGIN_AIRPORT_NAME', 'ORIGIN_STATE', 'DESTINATION_AIRPORT_NAME', 'DESTINATION_STATE', 'ORIGIN_AIRPORT_LAT', 'ORIGIN_AIRPORT_LON', 'DESTINATION_AIRPORT_LAT', 'DESTINATION_AIRPORT_LON'])

    print('cleaning nonCancelled...')
    nonCancelled_withallairports_NaN = nonCancelled.dropna(subset=['YEAR', 'MONTH', 'DAY', 'DAY_OF_WEEK','FLIGHT_NUMBER','SCHEDULED_DEPARTURE_LOCALTIME', 'SCHEDULED_TIME','ELAPSED_TIME', 'DISTANCE', 'SCHEDULED_ARRIVAL_LOCALTIME', 'CANCELLED'])
    nonCancelled_onlyflights = nonCancelled.dropna(subset=['DESTINATION_AIRPORT', 'ORIGIN_AIRPORT'])
    nonCancelled = nonCancelled_withallairports_NaN.dropna(subset=['AIRLINE', 'ORIGIN_AIRPORT', 'DESTINATION_AIRPORT','ORIGIN_AIRPORT_NAME', 'ORIGIN_STATE', 'DESTINATION_AIRPORT_NAME','DESTINATION_STATE', 'ORIGIN_AIRPORT_LAT', 'ORIGIN_AIRPORT_LON', 'DESTINATION_AIRPORT_LAT', 'DESTINATION_AIRPORT_LON'])
    
    print('concat dataframes')
    allFlights = pd.concat([nonCancelled, cancelled])
    allFlights_onlyflights = pd.concat([nonCancelled_onlyflights, cancelled_onlyflights])
    allFlights_withallairportsNaN = pd.concat([nonCancelled_withallairports_NaN, cancelled_withallairports_NaN])

    #save cleaned csv
    print('saving...')
    nonCancelled_onlyflights.to_csv('Data/cleaning/cleaned-data/flights_nonCancelled_NaN-onlyflights.csv', sep=',') #used in visual02 (heatmap - flightcount per day)
    nonCancelled.to_csv('Data/cleaning/cleaned-data/flights_nonCancelled-cleaned.csv', sep=',') #used in visual01 (Barchart w/ slider) and visual04 (chlorplethmap - states w/ highest arrival delay)
    nonCancelled_withallairports_NaN.to_csv('Data/cleaning/cleaned-data/flights_nonCancelled_withsomeNaN.csv', sep=',') #used in visual 05 (BubbleMap)
    allFlights_onlyflights.to_csv('Data/cleaning/cleaned-data/flights_allFlights_NaN_onlyflights.csv', sep=',') #used in visual03 (radarchart - airline performance)
    #allFlights_withallairportsNaN.to_csv('Data/cleaning/cleaned-data/flights_allFlights_NaN-cleaned.csv', sep=',') 
    #allFlights.to_csv('Data/cleaning/cleaned-data/flights_allFlights-cleaned.csv', sep=',')
 
run()
