'''
Visual02:
Heatmap that shows the number of long distance flights per day for the whole year. The hovertext additionally shows the day of the week and information about the overall distance travelled and the number of cancelled flights on that specific day.
The visualization also shows an annotation to inform the viewer on what is considered to be a long distance flight in this chart, when flights are considered to be delayed and an how cancelled flights are valued in terms of the distance travelled.
'''
from datetime import datetime
from numpy.core.numeric import NaN
import pandas as pd
import numpy as np
import plotly.graph_objects as go

#read csv with desired columns
df = pd.read_csv('Data/cleaning/cleaned-data/flights_nonCancelled-onlyflights-somemissingairports.csv', sep=',', usecols={'Unnamed: 0', 'YEAR', 'MONTH', 'DAY','AIRLINE','DISTANCE','ARRIVAL_DELAY'})


# testing if there are any rowsrows with NaN values left
# all values are in arrival delay - because the focus of this chart is the number of flights, i won't drop these rows, they just won't count into the 'delayed' count
testForNaNrows = df[df.isna().any(axis=1)]
print(testForNaNrows)

# creating a date column that merges year, month and day into a single date
df['DATE'] = pd.to_datetime({'year': df['YEAR'], 'month': df['MONTH'], 'day': df['DAY']})
df.drop(columns={'YEAR', 'MONTH', 'DAY'}, inplace=True)

#only flights with an arrival delay over 5 minutes are considered delayed (based on personal experience and preference - who really cares if your flight is like 3 minutes late?)
df['DELAYED'] = np.where(df.ARRIVAL_DELAY >5, True, NaN)

#series with number of flights per day (determined by value count of each date), sorted by date
series_datecount = df['DATE'].value_counts().sort_index()
series_delayed_count = df.groupby('DATE')['DELAYED'].count().sort_index()
series_distance_sum = df.groupby('DATE')['DISTANCE'].sum()

# series to dataframe, resetting index to get date as seperate column, renaming columns appropriately
dailyflights = pd.DataFrame(series_datecount)
dailyflights.reset_index(inplace=True)
dailyflights.rename(columns={'DATE':'flightcount', 'index':'date'}, inplace=True)
dailydelay = pd.DataFrame(series_delayed_count)
dailydelay.reset_index(inplace=True)
dailydelay.rename(columns={'DATE':'date', 'DELAYED':'delaycount'}, inplace=True)
dailyflights= dailyflights.merge(dailydelay, on='date')

dailydistance = pd.DataFrame(series_distance_sum)
dailydistance.reset_index(inplace=True)
dailydistance.rename(columns={'DATE':'date', 'DISTANCE':'distancesum'}, inplace=True)
dailyflights= dailyflights.merge(dailydistance, on='date')

'''
#Test to ensure that the output of df.groupby('DATE')['DELAYED'].count() correctly represents the number of delayed flights per day
print(df.groupby('DATE')['DELAYED'].count())
delayed = 0
punctual = 0
jan1st = df[df['DATE'] == datetime(2015,1,1)]
for index, row in jan1st.iterrows():
    if row['DELAYED'] == True:
        delayed += 1
    else:
        punctual += 1
print(punctual, delayed)
'''
#creating a string with additional information for the hover text
my_text= pd.to_datetime(dailyflights['date']).dt.strftime("%B %d, %Y (%A)") + '<br>Flights: ' + dailyflights['flightcount'].astype('str') + '<br>Delayed: '+ dailyflights['delaycount'].astype('str') + '<br>Distance: ' + dailyflights['distancesum'].astype('str') + ' miles'

fig = go.Figure(data=go.Heatmap(
        colorbar=dict(title=dict(text="Number Of Flights", side='right',),),
        #color based on flightcount
        z= dailyflights['flightcount'],
        #x-axis shows the days
        x= pd.to_datetime(dailyflights['date']).dt.day,
        #y-axis shows all months
        y= pd.to_datetime(dailyflights['date']).dt.month,
        #creating the hover-text based on the my_text string
        text= my_text,
        hovertemplate='%{text}<extra></extra>',
        #days where data is missing (e.g. dates that do not exist like February 29th) do not have a hovertext
        hoverongaps = False,
        colorscale='orrd'),
)
#updating axis to label axis with abbr. of months instead of simple integers for better readability
fig.update_yaxes(dtick=1, ticktext=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP', 'OCT','NOV','DEC'], tickvals=[1,2,3,4,5,6,7,8,9,10,11,12])
#labeling every day
fig.update_xaxes(dtick=1)
fig.update_layout(
    title=dict(text='Number of Long Distance Flights per Day (2015)'),
    xaxis_nticks=31,
    yaxis_nticks=12,
    width=1400,
    height=650,
    xaxis={'title': 'day'},
    yaxis={'title': 'month'},
    hovermode='closest',
    #creating an annotation box with information for the viewer
    annotations=[
            go.layout.Annotation(
                text='In this plot a flight is considered to be a long distance flight, if the distance travelled amounts to more than 1400 miles.<br>Flights are considered delayed when the delay upon arrival at the destination exceeds 5 minutes.<br>The distance of cancelled flights is valued at 0 miles.',
                align='right',
                showarrow=False,
                xref='paper',
                yref='paper',
                x=1,
                y=1.155,
            )
        ],
)
fig.write_html('out/HTML/Visual02-AnnotatedHeatmap/Visual02-AnnotatedHeatmap.html')
fig.show()
