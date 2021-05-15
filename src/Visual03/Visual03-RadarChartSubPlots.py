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

#creating list with desired values (count or sum of values per airline)
def creategroup (operation, groupby):
    if operation == 'count':
        if groupby == 'AIRLINE':
            group = df.groupby('AIRLINE')[groupby].count()
            return group
        else:
            group = df.groupby('AIRLINE')[groupby].count().sort_index()
            return group
    elif operation == 'sum':
        group = df.groupby('AIRLINE')[groupby].sum()
        return group
    else:
        print('Your using the wrong function. I only to sums and counts, sorry.')

#creating new dataframe with an additional column with count/sum of values per airline
def createnewcolsumcount (operation, groupby, dataframegroupByAirline):
    colasdf = pd.DataFrame(creategroup(operation, groupby))
    if groupby == 'AIRLINE':
        colasdf.rename(columns={'AIRLINE':'Count of Scheduled Flights'}, inplace = True)
    
    colasdf.reset_index(inplace=True)
    dataframegroupByAirline = dataframegroupByAirline.merge(colasdf, on='AIRLINE')
    return dataframegroupByAirline

groupByAirline = createnewcolsumcount('count', 'AIRLINE', groupByAirline)
groupByAirline = createnewcolsumcount('sum', 'ELAPSED_TIME', groupByAirline)
groupByAirline = createnewcolsumcount('sum', 'DISTANCE', groupByAirline)
groupByAirline = createnewcolsumcount('sum', 'ARRIVAL_DELAY', groupByAirline)
groupByAirline = createnewcolsumcount('count', 'CANCELLED', groupByAirline)
groupByAirline = createnewcolsumcount('count', 'ORIGIN_AIRPORT', groupByAirline)
groupByAirline = createnewcolsumcount('count', 'DESTINATION_AIRPORT', groupByAirline)

#creating percentage values of distance, elapsed time, delay, no. of cancelled flights and airports for airlines based on overall sum/count (to have a uniform basis for the range, bc/ the ranges of the absolut values differ a lot between the different dimensions)
percent_distance = groupByAirline['DISTANCE'] / groupByAirline.DISTANCE.sum() * 100
percent_elapsedtime = groupByAirline['ELAPSED_TIME'] / groupByAirline.ELAPSED_TIME.sum() * 100
percent_delay = groupByAirline['ARRIVAL_DELAY'] / groupByAirline.ARRIVAL_DELAY.sum() * 100
percent_cancelled = groupByAirline['CANCELLED'] / groupByAirline.CANCELLED.sum() * 100
percent_originairport = groupByAirline['ORIGIN_AIRPORT'] / groupByAirline.ORIGIN_AIRPORT.sum() * 100
percent_destinationairport = groupByAirline['DESTINATION_AIRPORT'] / groupByAirline.DESTINATION_AIRPORT.sum() * 100

# series to dataframe, resetting index to get airline as seperate column and merging with groupByAirline to get new column for percentage values
def createnewcolpercentage (percentagelist, dataframegroupByAirline):
    percentagedf = pd.DataFrame(percentagelist)
    percentagedf.reset_index(inplace=True)
    dataframegroupByAirline= dataframegroupByAirline.merge(percentagedf, left_index=True, right_index=True)
    return dataframegroupByAirline

groupByAirline = createnewcolpercentage(percent_distance,groupByAirline)
groupByAirline = createnewcolpercentage(percent_elapsedtime,groupByAirline)
groupByAirline = createnewcolpercentage(percent_delay,groupByAirline)
groupByAirline = createnewcolpercentage(percent_cancelled,groupByAirline)
groupByAirline = createnewcolpercentage(percent_originairport,groupByAirline)
groupByAirline = createnewcolpercentage(percent_destinationairport,groupByAirline)

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
'''
i know that especially in the last radar chart with the 3 smallest airlines the different planes are still a little hard to distinguish but i really did my best to find colors that improve the ability to differentiate between the different planes.
(please refer to the comment at the end of the script where the range for the radial axis is set for my reasoning)
'''

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

#creating a trace for each subplot - don't think i really have to explain this one...
# r are the values for all the different dimensions that are shown in the plot,
# theta are the names of these dimensions
# name is the name of the airline,
# the hovertemplate shows the numeric value of the share (r) for the category (theta), the airline name & how many flights the airline planned on flying
for i in range (3):
    fig.add_trace(go.Scatterpolar(
        r=[group_fig1.loc[i, 'Elapsed %'], group_fig1.loc[i, 'Distance %'], group_fig1.loc[i, 'Delay Time %'], group_fig1.loc[i, 'Cancelled %'], group_fig1.loc[i, 'Origin Airport Count %'], group_fig1.loc[i, 'Destination Airport Count %']],
        theta=categories,
        name= group_fig1.AIRLINE_NAME[i],
        fill='toself',
        line=dict(color=colors[i]),
        showlegend = True, 
        hovertemplate='Share: %{r}<br>Dimension: %{theta}<br>'+'Airline: {}<br>'.format(group_fig1.AIRLINE_NAME[i])+'No. of Scheduled Flights: {}'.format(group_fig1.loc[i, 'Count of Scheduled Flights'])+'<extra></extra>',),
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
        hovertemplate='Share: %{r}<br>Dimension: %{theta}<br>'+'Airline: {}<br>'.format(group_fig2.AIRLINE_NAME[i])+'No. of Scheduled Flights: {}'.format(group_fig2.loc[i, 'Count of Scheduled Flights'])+'<extra></extra>',),
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
        hovertemplate='Share: %{r}<br>Dimension: %{theta}<br>'+'Airline: {}<br>'.format(group_fig3.AIRLINE_NAME[i])+'No. of Scheduled Flights: {}'.format(group_fig3.loc[i, 'Count of Scheduled Flights'])+'<extra></extra>',),
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
        hovertemplate='Share: %{r}<br>Dimension: %{theta}<br>'+'Airline: {}<br>'.format(group_fig4.AIRLINE_NAME[i])+'No. of Scheduled Flights: {}'.format(group_fig4.loc[i, 'Count of Scheduled Flights'])+'<extra></extra>',),
        row=2,
        col=2
    )

fig.update_layout(
    polar = dict(
        radialaxis=dict(
        visible=True,
        ticks = '',
        ),
        angularaxis=dict(ticks='')
    ),
    showlegend=True,
    legend = dict(orientation='h', yanchor='top'), #legend at the bottom bc/ otherwise the heading would not be centered and bc/ the i don't consider the legend to be of major importance, because the airline names are shown upon hover as well
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
'''
i know that especially in the last radar chart with the 3 smallest airlines the different planes are still a little hard to distinguish, but this is kind of a trade-of for me -
i din't want a different range for the radar chart axis for each chart in an attempt to not skew perception of the performance differences when comparing airlines
(now i have one range for the 6 biggest airlines and one for the 6 smallest so at least these two could be easily compared and because it's impossible to use the same range for all charts without making them impossible to read)
'''
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
