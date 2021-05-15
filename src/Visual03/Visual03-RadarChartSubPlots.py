'''
Visual03:
Four Radarcharts that show performance of twelve airlines using the number of airports they service, the number of cancelled and diverted flights and the delay time of all flights
(displayed as percentages based on totals for plotting - otherwise the dimensions of the different categories would not match up, making a visual, that serves it's purpose (comparability) impossible)
'''
import pandas as pd
import plotly.graph_objects as go
from numpy.core.numeric import NaN
import numpy as np
from plotly.subplots import make_subplots

# read files & merging to get name of airline
df = pd.read_csv('Data/cleaning/cleaned-data/flights_allFlights_NaN_onlyflights.csv', sep=',', usecols=['AIRLINE','ELAPSED_TIME', 'DISTANCE','ARRIVAL_DELAY', 'CANCELLED','ORIGIN_AIRPORT', 'DESTINATION_AIRPORT'])

airline = pd.read_csv('Data/original-kaggle-flight-data/airlines.csv', sep=',')
df = df.merge(airline, left_on='AIRLINE', right_on='IATA_CODE', how='left').rename(columns={'AIRLINE_x':'AIRLINE','AIRLINE_y':'AIRLINE_NAME'}).copy()
df.drop(columns={'IATA_CODE'}, inplace=True)

#replace NaN with 0 in all columns
df.fillna(0, inplace=True)

# setting elapsed time, distance, delay and airports of all cancelled flights to 0 -> airline didn't fly so they're not counted
def setcancelledzero(col):
    df.loc[df.CANCELLED != 0, col] = 0

setcancelledzero('ELAPSED_TIME')
setcancelledzero('DISTANCE')
setcancelledzero('ARRIVAL_DELAY')
setcancelledzero('ORIGIN_AIRPORT')
setcancelledzero('DESTINATION_AIRPORT')

# setting delay of all flights that were faster than anticipated (negative delay) to 0 for better comparability
# setting cancelled column to NaN if flight has was not cancelled (for value_count)
df.loc[df.ARRIVAL_DELAY < 0, 'ARRIVAL_DELAY'] = 0
df['CANCELLED'] = np.where(df.CANCELLED == 0, NaN, 1)

#create dataframe with all airlines & airline names
groupByAirline = df.groupby(['AIRLINE', 'AIRLINE_NAME']).nunique().reset_index()
groupByAirline.drop(columns={'ELAPSED_TIME', 'DISTANCE', 'ARRIVAL_DELAY', 'CANCELLED', 'ORIGIN_AIRPORT', 'DESTINATION_AIRPORT'}, inplace=True)

#get overall number of flights (cancelled and non-cancelled)
series_flightcount = df.groupby('AIRLINE')['AIRLINE'].count()
# series to dataframe, resetting index to get date as seperate column, renaming columns appropriately and then merging with the groupByAirline Dataframe to get a new column und groupByAirline with the flightcount
scheduledflightcount = pd.DataFrame(series_flightcount)
scheduledflightcount.rename(columns={'AIRLINE':'Count of Scheduled Flights'}, inplace=True)
scheduledflightcount.reset_index(inplace=True)
groupByAirline= groupByAirline.merge(scheduledflightcount, on='AIRLINE')

# get sum of elapsed time, distance and delay per airline
series_elapsedtimesum = df.groupby('AIRLINE')['ELAPSED_TIME'].sum()
series_distancesum = df.groupby('AIRLINE')['DISTANCE'].sum()
series_delaysum = df.groupby('AIRLINE')['ARRIVAL_DELAY'].sum()
# get count of delayed flights, origin airports and destination airports per airline
series_cancelledcount = df.groupby('AIRLINE')['CANCELLED'].count().sort_index()
series_originairportcount = df.groupby('AIRLINE')['ORIGIN_AIRPORT'].count().sort_index()
series_destinationairportcount = df.groupby('AIRLINE')['DESTINATION_AIRPORT'].count().sort_index()

# series to dataframe, resetting index to get airline as seperate column and merging with groupByAirline to get new column for sum/count values
airlineelapsed = pd.DataFrame(series_elapsedtimesum)
airlineelapsed.reset_index(inplace=True)
groupByAirline= groupByAirline.merge(airlineelapsed, on='AIRLINE')

airlinedistance = pd.DataFrame(series_distancesum)
airlinedistance.reset_index(inplace=True)
groupByAirline= groupByAirline.merge(airlinedistance, on='AIRLINE')

airlinedelay = pd.DataFrame(series_delaysum)
airlinedelay.reset_index(inplace=True)
groupByAirline= groupByAirline.merge(airlinedelay, on='AIRLINE')

airlinecancelled = pd.DataFrame(series_cancelledcount)
airlinecancelled.reset_index(inplace=True)
groupByAirline= groupByAirline.merge(airlinecancelled, on='AIRLINE')

airlineoriginairport = pd.DataFrame(series_originairportcount)
airlineoriginairport.reset_index(inplace=True)
groupByAirline= groupByAirline.merge(airlineoriginairport, on='AIRLINE')

airlinedestinationairport = pd.DataFrame(series_destinationairportcount)
airlinedestinationairport.reset_index(inplace=True)
groupByAirline= groupByAirline.merge(airlinedestinationairport, on='AIRLINE')

#creating percentage values of distance, elapsed time, delay, no. of cancelled flights and airports for airlines based on overall number
percent_distance = groupByAirline['DISTANCE'] / groupByAirline.DISTANCE.sum() * 100
percent_elapsedtime = groupByAirline['ELAPSED_TIME'] / groupByAirline.ELAPSED_TIME.sum() * 100
percent_delay = groupByAirline['ARRIVAL_DELAY'] / groupByAirline.ARRIVAL_DELAY.sum() * 100
percent_cancelled = groupByAirline['CANCELLED'] / groupByAirline.CANCELLED.sum() * 100
percent_originairport = groupByAirline['ORIGIN_AIRPORT'] / groupByAirline.ORIGIN_AIRPORT.sum() * 100
percent_destinationairport = groupByAirline['DESTINATION_AIRPORT'] / groupByAirline.DESTINATION_AIRPORT.sum() * 100

# series to dataframe, resetting index to get airline as seperate column and merging with groupByAirline to get new column for percentage values
percent_distance = pd.DataFrame(percent_distance)
percent_distance.reset_index(inplace=True)
groupByAirline= groupByAirline.merge(percent_distance, left_index=True, right_index=True)

percent_elapsedtime = pd.DataFrame(percent_elapsedtime)
percent_elapsedtime.reset_index(inplace=True)
groupByAirline= groupByAirline.merge(percent_elapsedtime, left_index=True, right_index=True)

percent_delay = pd.DataFrame(percent_delay)
percent_delay.reset_index(inplace=True)
groupByAirline= groupByAirline.merge(percent_delay, left_index=True, right_index=True)

percent_cancelled = pd.DataFrame(percent_cancelled)
percent_cancelled.reset_index(inplace=True)
groupByAirline= groupByAirline.merge(percent_cancelled, left_index=True, right_index=True)

percent_originairport = pd.DataFrame(percent_originairport)
percent_originairport.reset_index(inplace=True)
groupByAirline= groupByAirline.merge(percent_originairport, left_index=True, right_index=True)

percent_destinationairport = pd.DataFrame(percent_destinationairport)
percent_destinationairport.reset_index(inplace=True)
groupByAirline= groupByAirline.merge(percent_destinationairport, left_index=True, right_index=True)

#dropping all redundant columns and renaming remainig columns appropriately
groupByAirline.drop(columns={'index_x', 'index_y', 'index_x', 'index_y', 'index_x', 'index_y'}, inplace=True)
groupByAirline.rename(columns={'ELAPSED_TIME_x':'Elapsed Time', 'DISTANCE_x':'Distance','ARRIVAL_DELAY_x':'Arrival Delay','CANCELLED_x':'Cancelled Flights', 'ORIGIN_AIRPORT_x':'Origin Airports', 'DESTINATION_AIRPORT_x':'Destination Airports','ELAPSED_TIME_y':'Share in Elapsed Time in Percent', 'DISTANCE_y':'Share in Distance in Percent', 'ARRIVAL_DELAY_y':'Share in Arrival Delays in Percent', 'CANCELLED_y':'Share in Number of Cancelled Flights in Percent', 'ORIGIN_AIRPORT_y':'Share in Number of Origin Airports in Percent', 'DESTINATION_AIRPORT_y':'Share in Number of Destination Airports in Percent'}, inplace=True)

#sorting by highest number of scheduled flights (measure for biggest airline)
groupByAirline.sort_values(by=['Count of Scheduled Flights'], ascending=False, inplace=True)
groupByAirline.reset_index(inplace=True)
groupByAirline.rename(columns={'Share in Elapsed Time in Percent':'Elapsed %', 'Share in Distance in Percent':'Distance %', 'Share in Arrival Delays in Percent':'Delay Time %', 'Share in Number of Cancelled Flights in Percent':'Cancelled %','Share in Number of Origin Airports in Percent':'Origin Airport Count %', 'Share in Number of Destination Airports in Percent':'Destination Airport Count %'}, inplace=True)

# creating visualizations

#get category-names from dataframe column names
categories = groupByAirline.loc[:,'Elapsed %':'Destination Airport Count %'].columns
colors = ['#FAAD89','#CABCE8','#75D55D','#ED9C87','#877099','#4BB386','#ACEBAB','#E36B6D','#7B1416','#736078','#F5C0B8','#79D494']

#creating subsets for each figure (and reordering subsets so the reorder the planes in the visualization to make them more distinguishable
group_fig1 = groupByAirline.iloc[:3]
group_fig1 = group_fig1.reindex([0,2,1])
group_fig1 = group_fig1.reset_index()
group_fig1.drop(columns={'level_0'}, inplace=True)

group_fig2 = groupByAirline.iloc[3:6]
group_fig2 = group_fig2.reindex([3,5,4])
group_fig2 = group_fig2.reset_index()
group_fig2.drop(columns={'level_0'}, inplace=True)

group_fig3 = groupByAirline.iloc[6:9]
group_fig3 = group_fig3.reset_index()
group_fig3.drop(columns={'level_0'}, inplace=True)

group_fig4 = groupByAirline.iloc[9:]
group_fig4 = group_fig4.reindex([9,11,10])
group_fig4 = group_fig4.reset_index()
group_fig4.drop(columns={'level_0'}, inplace=True)

# figure with 2 rows and 2 columns for the four subplots and setting titles for subplots
fig = make_subplots(
    rows=2,
    cols=2,
    subplot_titles=("The Big Three<br>United, American, Delta", "Southwest, Jet Blue, Alaska Airlines", "US Airways, Virgin, Spirit", "Smallest Airlines by Flightcount<br>Skywest, Hawaiian, Frontier"),
    specs=[[{"type": "polar"}, {"type": "polar"}],[{"type": "polar"}, {"type": "polar"}]]
)

#creating a trace for each subplot
for i in range (3):
    fig.add_trace(go.Scatterpolar(
        r=[group_fig1.loc[i, 'Elapsed %'], group_fig1.loc[i, 'Distance %'], group_fig1.loc[i, 'Delay Time %'], group_fig1.loc[i, 'Cancelled %'], group_fig1.loc[i, 'Origin Airport Count %'], group_fig1.loc[i, 'Destination Airport Count %']],
        theta=categories,
        name= group_fig1.AIRLINE_NAME[i],
        fill='toself',
        line=dict(color=colors[i]),
        showlegend = True, 
        hovertemplate='Share: %{r}<br>Dimension: %{theta}<br>'+'Airline: {}<br>'.format(group_fig1.AIRLINE_NAME[i])+'Flights Flown: {}'.format(group_fig1.loc[i, 'Count of Scheduled Flights'])+'<extra></extra>',),
        row=1,
        col=1
    )
    fig.add_trace(go.Scatterpolar(
        r=[group_fig2.loc[i, 'Elapsed %'], group_fig2.loc[i, 'Distance %'], group_fig2.loc[i, 'Delay Time %'], group_fig2.loc[i, 'Cancelled %'], group_fig2.loc[i, 'Origin Airport Count %'], group_fig2.loc[i, 'Destination Airport Count %']],
        theta=categories,
        name= group_fig2.AIRLINE_NAME[i],
        fill='toself',
        line=dict(color=colors[i+3]),
        showlegend = True, 
        hovertemplate='Share: %{r}<br>Dimension: %{theta}<br>'+'Airline: {}<br>'.format(group_fig2.AIRLINE_NAME[i])+'Flights Flown: {}'.format(group_fig2.loc[i, 'Count of Scheduled Flights'])+'<extra></extra>',),
        row=1,
        col=2
    )
    fig.add_trace(go.Scatterpolar(
        r=[group_fig3.loc[i, 'Elapsed %'], group_fig3.loc[i, 'Distance %'], group_fig3.loc[i, 'Delay Time %'], group_fig3.loc[i, 'Cancelled %'], group_fig3.loc[i, 'Origin Airport Count %'], group_fig3.loc[i, 'Destination Airport Count %']],
        theta=categories,
        name= group_fig3.AIRLINE_NAME[i],
        fill='toself',
        line=dict(color=colors[i+6]),
        showlegend = True, 
        hovertemplate='Share: %{r}<br>Dimension: %{theta}<br>'+'Airline: {}<br>'.format(group_fig3.AIRLINE_NAME[i])+'Flights Flown: {}'.format(group_fig3.loc[i, 'Count of Scheduled Flights'])+'<extra></extra>',),
        row=2,
        col=1
    )
    fig.add_trace(go.Scatterpolar(
        r=[group_fig4.loc[i, 'Elapsed %'], group_fig4.loc[i, 'Distance %'], group_fig4.loc[i, 'Delay Time %'], group_fig4.loc[i, 'Cancelled %'], group_fig4.loc[i, 'Origin Airport Count %'], group_fig4.loc[i, 'Destination Airport Count %']],
        theta=categories,
        name= group_fig4.AIRLINE_NAME[i],
        fill='toself',
        line=dict(color=colors[i+9]),
        showlegend = True, 
        hovertemplate='Share: %{r}<br>Dimension: %{theta}<br>'+'Airline: {}<br>'.format(group_fig4.AIRLINE_NAME[i])+'Flights Flown: {}'.format(group_fig4.loc[i, 'Count of Scheduled Flights'])+'<extra></extra>',),
        row=2,
        col=2
    )

fig.update_layout(
    polar = dict(
        radialaxis=dict(
        visible=True,
        ticks = '',
        range = [0,32],
        ),
        angularaxis=dict(ticks='')
    ),
    showlegend=True,
    legend = dict(orientation='h', yanchor='top'),
    title_text = 'Airline Performance Comparison',
    title_y = 0.985,
    title_x = 0.5,
    title_xanchor = 'center',
    hovermode='closest',
    annotations=[
        go.layout.Annotation(
                y=1.02
            ),
        go.layout.Annotation(
                y=1.02
            ),
        go.layout.Annotation(
                y=0.4
            ),
        go.layout.Annotation(
                y=0.4
    
            ),
        ],
)

#setting ranges for each plot
#the two plots for the biggest airlines have the same range and the two plots for the smallest airlines have the same range to imporve comparability without making the plots undecipherable because the range is too big for the smaller airlines
fig.update_polars(
    radialaxis=dict(range = [0,32]),
    row = 1,
    col = 1
)
fig.update_polars(
    radialaxis=dict(range = [0,32]),
    row = 1,
    col = 2
)
fig.update_polars(
    radialaxis=dict(range = [0,6.5]),
    row = 2,
    col = 1
)
fig.update_polars(
    radialaxis=dict(range = [0,6.5]),
    row = 2,
    col = 2
)

fig.update_layout(template='none')

fig.write_html('out/HTML/Visual03-RadarChartSubPlots/Visual03-RadarChartSubPlots.html')
fig.show()
