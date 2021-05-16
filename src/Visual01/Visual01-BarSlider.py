'''
Visual01:
Barchart that shows the airports with the highest average departure delays and with a slider to choose how many airports are shown in the visualization (e.g. the top 10 airports with the highest departure delays)
'''
import pandas as pd
import plotly.graph_objects as go

#read dataframe with nonCancelled flights (not like that's obvious)
df = pd.read_csv('Data/cleaning/cleaned-data/flights_nonCancelled-onlyflights-withairports.csv', sep=',', usecols = {'Unnamed: 0', 'AIRLINE', 'DEPARTURE_DELAY','ARRIVAL_DELAY','ORIGIN_AIRPORT','ORIGIN_AIRPORT_NAME','DESTINATION_AIRPORT','DESTINATION_AIRPORT_NAME'})
airports = pd.read_csv('Data/original-kaggle-flight-data/airports.csv', sep=',')

#new dataframes for all arriving and for all departing flights (grouped by airport)
ArrivingPerAirport = df.groupby(["DESTINATION_AIRPORT"]).nunique().reset_index()
ArrivingPerAirport = ArrivingPerAirport.rename(columns={'Unnamed: 0':'flightcount'}).reset_index()
ArrivingPerAirport.drop(columns={'index', 'AIRLINE', 'ORIGIN_AIRPORT','DEPARTURE_DELAY','ORIGIN_AIRPORT_NAME','DESTINATION_AIRPORT_NAME'}, inplace=True)

# adding airport name
airport_name = airports.groupby(['IATA_CODE'], as_index=False).agg({'AIRPORT': 'first'})
ArrivingPerAirport = ArrivingPerAirport.merge(airport_name, left_on='DESTINATION_AIRPORT', right_on = 'IATA_CODE')
ArrivingPerAirport.rename(columns={'AIRPORT':'DESTINATION_AIRPORT_NAME'})

#new column with average arrival delay and median delay
ArrivalDelayAvg = pd.DataFrame(df.groupby(['DESTINATION_AIRPORT'])['ARRIVAL_DELAY'].mean())
ArrivingPerAirport = ArrivingPerAirport.merge(ArrivalDelayAvg, on='DESTINATION_AIRPORT')
ArrivingPerAirport.drop(columns={'ARRIVAL_DELAY_x'}, inplace=True)
ArrivingPerAirport.rename(columns={'ARRIVAL_DELAY_y':'ArrivalDelayAvg'}, inplace=True)

ArrivalDelayMedian = pd.DataFrame(df.groupby(['DESTINATION_AIRPORT'])['ARRIVAL_DELAY'].median())
ArrivingPerAirport = ArrivingPerAirport.merge(ArrivalDelayMedian, on='DESTINATION_AIRPORT')
ArrivingPerAirport.rename(columns={'ARRIVAL_DELAY':'ArrivalDelayMedian'}, inplace=True)

#new column with average and median departure delay
DepartingPerAirport = df.groupby(["ORIGIN_AIRPORT"]).nunique().reset_index()
DepartingPerAirport = DepartingPerAirport.rename(columns={'Unnamed: 0':'flightcount'}).reset_index()
DepartingPerAirport.drop(columns={'index', 'AIRLINE', 'DESTINATION_AIRPORT','ARRIVAL_DELAY','ORIGIN_AIRPORT_NAME','DESTINATION_AIRPORT_NAME'}, inplace=True)

DepartingPerAirport = DepartingPerAirport.merge(airport_name, left_on='ORIGIN_AIRPORT', right_on = 'IATA_CODE')
DepartingPerAirport.rename(columns={'AIRPORT':'ORIGIN_AIRPORT_NAME'})

DepartureDelayAvg = pd.DataFrame(df.groupby(['ORIGIN_AIRPORT'])['DEPARTURE_DELAY'].mean())
DepartingPerAirport = DepartingPerAirport.merge(DepartureDelayAvg, on='ORIGIN_AIRPORT')
DepartingPerAirport.drop(columns={'DEPARTURE_DELAY_x'}, inplace=True)
DepartingPerAirport.rename(columns={'DEPARTURE_DELAY_y':'DepartureDelayAvg'}, inplace=True)

DepartureDelayMedian = pd.DataFrame(df.groupby(['ORIGIN_AIRPORT'])['DEPARTURE_DELAY'].median())
DepartingPerAirport = DepartingPerAirport.merge(DepartureDelayMedian, on='ORIGIN_AIRPORT')
DepartingPerAirport.rename(columns={'DEPARTURE_DELAY':'DepartureDelayMedian'}, inplace=True)

#could i have put all of the above in a function to make the code shorter? probably. did i want to? no. please forgive me - i know it's a little messy, but it does the job.

#combining both dataframes to new dataframe with all flights
relevantAirports = ArrivingPerAirport.merge(DepartingPerAirport, left_on='DESTINATION_AIRPORT', right_on='ORIGIN_AIRPORT')
relevantAirports.drop(columns={'DESTINATION_AIRPORT', 'IATA_CODE_x', 'IATA_CODE_y', 'AIRPORT_x'}, inplace=True)
relevantAirports.rename(columns={'AIRPORT_y':'AIRPORT_NAME','ORIGIN_AIRPORT':'AIRPORT', 'ORIGIN_AIRPORT_NAME':'AIRPORT_NAME', 'flightcount_x':'Sum_Arriving', 'flightcount_y':'Sum_Departing'}, inplace=True)

fig = go.Figure()

#creating empty lists to append to in for-loop
#topDelayedGroup and visibilitylist start with an empty list item to fill index 0, because the list will be accessed starting at index 1
topDelayedGroup = [[]]
steps = []
visibilitylist = [[]]
#list with all false values in same length as the dataframe from the for-loop will be
visibilityval = [False for n in range(len(relevantAirports.index))]

'''
This is were it get's a litte complicated and tricky (i would know, it took me forever to actually fix the logic in this mess of a for-loop). please just bear with me, i promise it works
what i'm doing in short:
  1.  sorting relevantairports by the highest average departure delay (and as a secondary sort my the number of flights departing from the airport)
  2.  then i'm dropping all rows below the index value i in each iterration to create a new dataframe in each iterration
  3.  i add a new column to the newly created dataframe that basically tells you which iteration the dataframe belongs to (first iteration: the value in the column would be 'Top 1', second iteration: the value would be 'Top 2' ans so on)
  4.  now i'm appending the dataframe to a list
      i now have a list of dataframes - in the first dataframe is only one row with the airport with the highest delay. in the second one are two rows with the airports with the two highest delays and so on. in the last list entry is a dataframe with all airports
  5.  i create a boolean list which is appended to visibilitylist, which is later used to mark which trace is visible based on the position of the slider
  6.  i create a trace for each slider step using the list of dataframes
  7.  i create a dict for each slider step
'''

for i in range (1,len(relevantAirports.index)):
    # new dataframe where entries of relevantAirports are sorted by the average departure delay (highest first) (and if multiple rows have the same departure delay, by the number of flights departing from the airport)
    # dropping all rows except the ones in rows 0 to i: new dataframe with airports with i highest avg. departure delay - e.g. i=10 will create a dataframe with the top 10 airports with the highest avg. departure delay
    relevantByDepartureDelay = relevantAirports.sort_values(by=['DepartureDelayAvg', 'Sum_Departing'], ascending=False).reset_index().drop(relevantAirports.index[i:])
    #print(relevantByDepartureDelay)
    # creating a new row in the dataframe to mark the iteration (Top n meaning the data frame shows the top n airports with the highest delay) and then appending the newly created dataframe to the topDelayedGroup list
    relevantByDepartureDelay['Top n'] = 'Top {}'.format(i)
    topDelayedGroup.append(relevantByDepartureDelay)
    
    # creating lists with boolean values (later used to mark which trace is visible) and concatenating them to one list
    previsibility = [False for n in range(i-1)]
    postvisibility = [False for x in range(i+1, len(relevantAirports.index))]
    truevisible = [True]
    visibilityval = [] + previsibility + truevisible + postvisibility
    #appending the newly created lists to another list
    visibilitylist.append(visibilityval)

    # creating a trace for each slider step
    fig.add_trace(go.Bar(
        #accessing the list topDelayedGroup and getting the airport and departuredelayavg column from the dataframe at the correct position
        x=topDelayedGroup[i]['AIRPORT'],
        y=topDelayedGroup[i]['DepartureDelayAvg'],
        name='Top {} Airports by Highest Departure Delay'.format(i),
        #marking the trace for slider position 10 (the top 10 airports with highest avg. departure delay) as visible and all others as invisible
        visible = visibilityval[9],
        # coloing the bars in a colorscale that is dependent on the average departure delay
        marker={'color': topDelayedGroup[i]['DepartureDelayAvg'], 'colorscale':[[0, '#DA6F6F'], [1, '#6A0909']]},
        # hovertext will show which airport (name) is shown, how many flights departed from that airport, the median departure delay and the exact value of the average departure delay
        text = topDelayedGroup[i]['AIRPORT_NAME']+'<br>No. Of Flights Departing: '+topDelayedGroup[i]['Sum_Departing'].astype('str')+'<br>Median Departure Delay: ' + topDelayedGroup[i]['DepartureDelayMedian'].astype('str'),
        hovertemplate = 'Airport: %{text}' +'<br>Average Departure Delay: %{y}<extra></extra>'
        ))
    # creating the steps for the slider    
    step = dict(label = topDelayedGroup[i]['Top n'].iloc[0], method = "update",args = [{"visible": visibilitylist[i]}])
    steps.append(step)

# wooo we finally got through this mess of a for loop（〜^∇^)〜 hope you didn't get lost along the way

# creating the sliders
sliders = [dict(
    # when the page is first loaded the slider is at the 'Top 10' position
    active=9,
    pad={"t": 50},
    steps=steps,
    bgcolor = '#DA6F6F',
    activebgcolor = '#6A0909'
)]

fig.update_layout(
    plot_bgcolor="white",
    xaxis=dict(showgrid=True),
    yaxis = dict(gridcolor = '#AFA8A8',),
    sliders = sliders,
    title_text = 'Airports With Highest Average Departure Delays<br>Use the slider to select how many airports you want to see.'.format(),
)
# saving html code of the figure
fig.write_html('out/HTML/Visual01-BarSlider/Visual01-BarSlider.html')
fig.show()

