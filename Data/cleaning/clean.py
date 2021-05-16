from numpy.core.numeric import NaN
import pandas as pd
import numpy as np

#read raw file with airports.. obviously
airports = pd.read_csv('Data/original-kaggle-flight-data/airports.csv', sep=',', usecols=['IATA_CODE', 'AIRPORT', 'STATE' , 'LATITUDE', 'LONGITUDE'])

def run():
    #read raw file with flights (who would have guessed?)
    print('reading csv')
    df = pd.read_csv('Data/original-kaggle-flight-data/flights.csv', sep=',', usecols=['YEAR', 'MONTH', 'DAY', 'DAY_OF_WEEK', 'AIRLINE', 'FLIGHT_NUMBER', 'ORIGIN_AIRPORT', 'DESTINATION_AIRPORT', 'DISTANCE', 'SCHEDULED_DEPARTURE','DEPARTURE_DELAY', 'SCHEDULED_TIME', 'ELAPSED_TIME', 'SCHEDULED_ARRIVAL', 'ARRIVAL_DELAY', 'DIVERTED', 'CANCELLED', 'CANCELLATION_REASON', 'AIR_SYSTEM_DELAY', 'SECURITY_DELAY', 'AIRLINE_DELAY', 'LATE_AIRCRAFT_DELAY', 'WEATHER_DELAY'], parse_dates=['SCHEDULED_DEPARTURE', 'SCHEDULED_ARRIVAL'])
    print(df.shape)

    #renaming columns for clarification
    #i never actually ended up using these, but when I was cleaning the data i thought it might come in handy. it didn't... but here ya go anyways because otherwise i would have had to adjust all the other code. also you could still technically use it in code if you wanted to ¯\_(ツ)_/¯
    df = df.rename(columns={'SCHEDULED_DEPARTURE':'SCHEDULED_DEPARTURE_LOCALTIME', 'SCHEDULED_ARRIVAL':'SCHEDULED_ARRIVAL_LOCALTIME'}).copy()

    #filtering out long distance flights (longer than 1400 miles) (to Florian: the threshold is 1400 because you used the same one)
    #mainly to reduce the dataset because i ain't waiting an hour for the cleaning to complete just because i wanted to use the data of almost 6 million flights
    print('filtering data')
    df = df[df['DISTANCE']>1400]
    print(df.shape)

    #creating datetime out of scheduled-time columns (to Florian: as seen in your data cleaning)
    print('formatting datum data')
    df['SCHEDULED_DEPARTURE_LOCALTIME'] = pd.to_datetime(df['SCHEDULED_DEPARTURE_LOCALTIME'], errors='coerce', format = '%H%M')
    df['SCHEDULED_DEPARTURE_LOCALTIME'] = df['SCHEDULED_DEPARTURE_LOCALTIME'].apply(lambda dt: dt.replace(year=2015))
    df['SCHEDULED_ARRIVAL_LOCALTIME'] = pd.to_datetime(df['SCHEDULED_ARRIVAL_LOCALTIME'], errors='coerce', format = '%H%M')
    df['SCHEDULED_ARRIVAL_LOCALTIME'] = df['SCHEDULED_ARRIVAL_LOCALTIME'].apply(lambda dt: dt.replace(year=2015))

    #new column where adjustment for time difference is removed
    delta = pd.to_timedelta(df['SCHEDULED_TIME'],'minute')
    df['SCHEDULED_ARRIVAL_ORIGINTIME'] = df['SCHEDULED_DEPARTURE_LOCALTIME'] + delta
    print(df.shape)
    
    '''
    if you're reading this.. wow. surprised you're actually checking out my data cleaning, but i respect the effort 
        ∧__∧
      （｀•ω• )づ__∧
      （つ　 /( •ω•。)
       しーＪ  (nnノ) pat pat
    '''
    #merging with airports file
    #note that the merge is an outer merge so I can include all airports. In the NaN cleaning I will create a new dataframe where these rows (that do not have a flight associated with them) are removed.
    print('merging with airports.csv')
    airportflights = df.merge(airports, left_on='ORIGIN_AIRPORT', right_on='IATA_CODE', how='outer').copy().drop(columns=['ORIGIN_AIRPORT']).copy()
    airportflights = airportflights.rename(columns={'IATA_CODE':'ORIGIN_AIRPORT','AIRPORT':'ORIGIN_AIRPORT_NAME', 'CITY':'ORIGIN_CITY', 'STATE':'ORIGIN_STATE', 'LATITUDE':'ORIGIN_AIRPORT_LAT', 'LONGITUDE':'ORIGIN_AIRPORT_LON'}).copy()
    airportflights = airportflights.merge(airports, left_on='DESTINATION_AIRPORT', right_on='IATA_CODE', how='outer').drop(columns=['DESTINATION_AIRPORT']).copy()
    airportflights = airportflights.rename(columns={'IATA_CODE':'DESTINATION_AIRPORT','AIRPORT':'DESTINATION_AIRPORT_NAME', 'CITY':'DESTINATION_CITY', 'STATE':'DESTINATION_STATE', 'LATITUDE':'DESTINATION_AIRPORT_LAT', 'LONGITUDE':'DESTINATION_AIRPORT_LON'}).copy()
    print('Airportflights: ', airportflights.shape)
    #new dataframes with cancelled flights & without cancelled flights (just i have to filter out less when creating visualizations that only use one of them)
    print('separating cancelled and non-cancelled flights')
    cancelled = airportflights[airportflights['CANCELLED'] == 1]
    nonCancelled = airportflights[airportflights['CANCELLED'] != 1] #also includes rows with airports only
    print('Cancelled:',cancelled.shape)
    print('nonCancelled:',nonCancelled.shape)

    #cleaning
    print('cleaning NANs')
    
    '''
    short explanation by suffix of dataframe names:
    withallairports_NaN:
        doesn't remove all NaN rows in all columns so 1.) i can keep rows that only contain airports and have no flight associated with it (to plot the airports even if there are no relevant flights connected to it)
        and 2.) to keep rows where information is missing that might not be needed in all visualizations
    onlyflights:
        removes rows without airports from withallairports_NaN dataframes
    no-suffix:
        all NaNs removed
    '''
    
    print('cleaning cancelled...')
    cancelled_onlyflights = cancelled.dropna(subset=['YEAR', 'MONTH', 'DAY'])

    cancelled_onlyflights_withairports = cancelled_onlyflights.dropna(subset=['ORIGIN_AIRPORT', 'DESTINATION_AIRPORT'])

    #checking which columns contain nan
    null_columns=cancelled_onlyflights_withairports.columns[cancelled_onlyflights_withairports.isnull().any()]
    print(cancelled_onlyflights_withairports[null_columns].isnull().sum())

    print('Cancelled cancelled_onlyflights: ',cancelled_onlyflights.shape)
    print('Cancelled cancelled_onlyflightswithairports: ',cancelled_onlyflights_withairports.shape)
    
    print('cleaning nonCancelled...')
    nonCancelled_onlyflights = nonCancelled.dropna(subset=['YEAR','MONTH', 'DAY'])
    nonCancelled_onlyflights_withairports = nonCancelled_onlyflights.dropna(subset=['ORIGIN_AIRPORT', 'DESTINATION_AIRPORT', 'ELAPSED_TIME'])

    print('non-Cancelled cancelled_onlyflights: ',nonCancelled_onlyflights.shape)
    print('non-Cancelled cancelled_onlyflightswithairports: ',nonCancelled_onlyflights_withairports.shape)

    #checking which columns contain nan
    null_columns=nonCancelled_onlyflights_withairports.columns[nonCancelled_onlyflights_withairports.isnull().any()]
    print(nonCancelled_onlyflights_withairports[null_columns].isnull().sum())

    print('concat dataframes')
    allFlights_withairports = pd.concat([cancelled_onlyflights_withairports, cancelled_onlyflights_withairports])
    allFlights_onlyflights = pd.concat([nonCancelled_onlyflights, cancelled_onlyflights])
    allFlights_withallairportsNaN = pd.concat([nonCancelled, cancelled])

    #save cleaned csv
    print('saving...')
    nonCancelled_onlyflights_withairports.to_csv('Data/cleaning/cleaned-data/flights_nonCancelled-onlyflights-withairports.csv', sep=',') ##used in visual01 (Barchart w/ slider), used in visual04 (chlorplethmap - states w/ highest arrival delay), used in visual 05 (BubbleMap)
    nonCancelled_onlyflights.to_csv('Data/cleaning/cleaned-data/flights_nonCancelled-onlyflights-somemissingairports.csv', sep=',') #used in visual02 (heatmap - flightcount per day)
    allFlights_onlyflights.to_csv('Data/cleaning/cleaned-data/flights_allFlights_onlyflights-somemissingairports.csv', sep=',') #used in visual03 (radarchart - airline performance)
    nonCancelled.to_csv('Data/cleaning/cleaned-data/flights_nonCancelled_withallNaNs.csv', sep=',') #used in visual 05 (BubbleMap),

run()
