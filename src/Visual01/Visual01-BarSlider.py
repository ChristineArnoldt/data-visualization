'''
Visual01:
Barchart that shows the airports with the highest average departure delays and with a slider to choose how many airports are shown in the visualization (e.g. the top 10 airports with the highest departure delays)
'''
import pandas as pd
import plotly.graph_objects as go

#read dataframe with nonCancelled flights
df = pd.read_csv('Data/cleaning/cleaned-data/flights_nonCancelled-cleaned.csv', sep=',', usecols = {'Unnamed: 0', 'AIRLINE', 'DEPARTURE_DELAY','ARRIVAL_DELAY','ORIGIN_AIRPORT','ORIGIN_AIRPORT_NAME','DESTINATION_AIRPORT','DESTINATION_AIRPORT_NAME'})

#new dataframes for all arriving and for all departing flights (grouped by airport) with a new column with average arrival or departure delay respectively, all other columns removed
ArrivingPerAirport = df.groupby(["DESTINATION_AIRPORT"]).nunique().reset_index()
ArrivingPerAirport = ArrivingPerAirport.rename(columns={'Unnamed: 0':'flightcount'}).reset_index()
ArrivingPerAirport.drop(columns={'index', 'AIRLINE', 'ORIGIN_AIRPORT','DEPARTURE_DELAY','ORIGIN_AIRPORT_NAME','DESTINATION_AIRPORT_NAME'}, inplace=True)
ArrivalDelayAvg = pd.DataFrame(df.groupby(['DESTINATION_AIRPORT'])['ARRIVAL_DELAY'].mean())
ArrivingPerAirport = ArrivingPerAirport.merge(ArrivalDelayAvg, on='DESTINATION_AIRPORT')
ArrivingPerAirport.drop(columns={'ARRIVAL_DELAY_x'}, inplace=True)
ArrivingPerAirport.rename(columns={'ARRIVAL_DELAY_y':'ArrivalDelayAvg'}, inplace=True)

DepartingPerAirport = df.groupby(["ORIGIN_AIRPORT"]).nunique().reset_index()
DepartingPerAirport = DepartingPerAirport.rename(columns={'Unnamed: 0':'flightcount'}).reset_index()
DepartingPerAirport.drop(columns={'index', 'AIRLINE', 'DESTINATION_AIRPORT','ARRIVAL_DELAY','ORIGIN_AIRPORT_NAME','DESTINATION_AIRPORT_NAME'}, inplace=True)
DepartureDelayAvg = pd.DataFrame(df.groupby(['ORIGIN_AIRPORT'])['DEPARTURE_DELAY'].mean())
DepartingPerAirport = DepartingPerAirport.merge(DepartureDelayAvg, on='ORIGIN_AIRPORT')
DepartingPerAirport.drop(columns={'DEPARTURE_DELAY_x'}, inplace=True)
DepartingPerAirport.rename(columns={'DEPARTURE_DELAY_y':'DepartureDelayAvg'}, inplace=True)

#combining both dataframes to new dataframe with all flights
relevantAirports = ArrivingPerAirport.merge(DepartingPerAirport, left_on='DESTINATION_AIRPORT', right_on='ORIGIN_AIRPORT')
relevantAirports.drop(columns={'DESTINATION_AIRPORT'}, inplace=True)
relevantAirports.rename(columns={'ORIGIN_AIRPORT':'AIRPORT', 'flightcount_x':'Sum_Arriving', 'flightcount_y':'Sum_Departing'}, inplace=True)

fig = go.Figure()

#creating empty lists to append to in for-loop
#topDelayedGroup and visibilitylist start with an empty list item to fill index 0, because the list will be accessed starting at index 1
topDelayedGroup = [[]]
steps = []
visibilitylist = [[]]
#list with all false values in same length as the dataframe from the for-loop will be
visibilityval = [False for n in range(len(relevantAirports.index))]

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
        # hovertext will show which trace is selected (e.g. Top 10), which airport is shown and the exact value of the departure delay
        hovertemplate = 'Top {}<br>'.format(i)+'Airport: %{x}'+'<br>Average Departure Delay: %{y}<extra></extra>'
        ))
    # creating the steps for the slider    
    step = dict(label = topDelayedGroup[i]['Top n'].iloc[0], method = "update",args = [{"visible": visibilitylist[i]}])
    steps.append(step)
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

