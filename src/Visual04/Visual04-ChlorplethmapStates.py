'''
Visual04:
US-Map where states are colored based on the average arrival delay of flights arriving in that state.
'''
import pandas as pd
import plotly.graph_objects as pgo

#read shit
df = pd.read_csv('Data/cleaning/cleaned-data/flights_nonCancelled-cleaned.csv', usecols={'Unnamed: 0', 'ARRIVAL_DELAY','ORIGIN_AIRPORT','ORIGIN_AIRPORT_NAME', 'DESTINATION_AIRPORT_NAME', 'ORIGIN_STATE', 'DESTINATION_STATE', 'ORIGIN_AIRPORT_LAT', 'ORIGIN_AIRPORT_LON', 'DESTINATION_AIRPORT_LAT', 'DESTINATION_AIRPORT_LON'})
usstates = pd.read_csv('https://raw.githubusercontent.com/jasonong/List-of-US-States/master/states.csv')

#create csv with States and number of flights per state
ArrivingPerState = df.groupby(['DESTINATION_STATE']).nunique().reset_index()
ArrivingPerState = ArrivingPerState.merge(usstates, left_on='DESTINATION_STATE', right_on='Abbreviation', how='left')
ArrivingPerState.rename(columns={'Unnamed: 0':'flightcount', 'State':'State_Name'}, inplace=True)
ArrivingPerState.drop(columns={'ARRIVAL_DELAY','ORIGIN_AIRPORT','ORIGIN_AIRPORT_NAME', 'DESTINATION_AIRPORT_NAME', 'ORIGIN_STATE', 'ORIGIN_AIRPORT_LAT', 'ORIGIN_AIRPORT_LON', 'DESTINATION_AIRPORT_LAT', 'DESTINATION_AIRPORT_LON', 'Abbreviation'},inplace=True),

#new dataframe with the arrival delay per state - merging with ArrivingPerState
arrivalDelay = df.groupby(['DESTINATION_STATE'])['ARRIVAL_DELAY'].sum().reset_index()
ArrivingPerState = ArrivingPerState.merge(arrivalDelay, on='DESTINATION_STATE')

#new dataframe with the average arrival delay per state - merging with ArrivingPerState
arrivalDelayAvg = df.groupby(['DESTINATION_STATE'])['ARRIVAL_DELAY'].mean().reset_index()
ArrivingPerState = ArrivingPerState.merge(arrivalDelayAvg, on='DESTINATION_STATE')
ArrivingPerState.rename(columns={'ARRIVAL_DELAY_x':'ArrivalDelay', 'ARRIVAL_DELAY_y':'ArrivalDelayAvg'}, inplace=True)
print(ArrivingPerState)

#create map
fig = pgo.Figure()
fig.add_trace(pgo.Choropleth(
    #labeling colorbar
    colorbar=dict(title=dict(text="Average Arrival Delay", side='right',),),
    locationmode='USA-states',
    locations=ArrivingPerState['DESTINATION_STATE'],
    z=ArrivingPerState['ArrivalDelayAvg'],
    colorscale="OrRd",
    #setting the hovertext to show the full state name
    text = ArrivingPerState['State_Name'],
    hovertemplate='In %{text} long distance flights landed with an average delay of %{z} minutes.<br><extra></extra>',
    
))
fig.update_layout(
    geo=dict(
        lakecolor="cornflowerblue",
        scope='usa',
        bgcolor="white",
    ),
    plot_bgcolor="white",
    title=dict(text="Average Flight Delay Of Long Distance Flights Upon Arrival", xanchor='center', x=0.5)
)

fig.write_html('out/HTML/Visual04-ChlorplethmapStates/Visual04-ChlorplethmapStates.html')
fig.show()