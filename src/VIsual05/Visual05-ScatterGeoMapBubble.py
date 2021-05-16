'''
Visual05:
Bubble Trace Map that shows airports in the US, where the bubbles representing the airports vary in size based on the number of flights arriving and
in color based on the average arrival delay of flights at that airport.
'''
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

#read file
df = pd.read_csv('Data/cleaning/cleaned-data/flights_nonCancelled-onlyflights-withairports.csv', usecols={'Unnamed: 0','ORIGIN_AIRPORT', 'ORIGIN_AIRPORT_NAME', 'DESTINATION_AIRPORT', 'DESTINATION_AIRPORT_NAME', 'ORIGIN_AIRPORT_LON', 'ORIGIN_AIRPORT_LAT', 'DESTINATION_AIRPORT_LON', 'DESTINATION_AIRPORT_LAT', 'ARRIVAL_DELAY'})
allairports = pd.read_csv('Data/cleaning/cleaned-data/flights_nonCancelled_withallNaNs.csv', usecols={'Unnamed: 0','ORIGIN_AIRPORT', 'ORIGIN_AIRPORT_NAME', 'DESTINATION_AIRPORT', 'DESTINATION_AIRPORT_NAME', 'ORIGIN_AIRPORT_LON', 'ORIGIN_AIRPORT_LAT', 'DESTINATION_AIRPORT_LON', 'DESTINATION_AIRPORT_LAT', 'ARRIVAL_DELAY'})

print(df.head())

#removing rows without an origin airport (and by doing so also removing rows without a destination airport)
df.dropna(subset=['ORIGIN_AIRPORT'], inplace=True)

#getting count of flights arriving per destination airport
ArrivingFlightsPerAirport = df.groupby(['DESTINATION_AIRPORT']).nunique().reset_index()
ArrivingFlightsPerAirport.drop(columns={'ORIGIN_AIRPORT', 'ORIGIN_AIRPORT_NAME','DESTINATION_AIRPORT_NAME', 'ORIGIN_AIRPORT_LON', 'ORIGIN_AIRPORT_LAT', 'DESTINATION_AIRPORT_LON', 'DESTINATION_AIRPORT_LAT', 'ARRIVAL_DELAY'},inplace=True),
ArrivingFlightsPerAirport.rename(columns={'Unnamed: 0': 'flightcount'}, inplace=True)

#getting average arrival delay per airport
arrivalDelayAvg = df.groupby(['DESTINATION_AIRPORT'])['ARRIVAL_DELAY'].mean().reset_index()
ArrivingFlightsPerAirport = ArrivingFlightsPerAirport.merge(arrivalDelayAvg, on='DESTINATION_AIRPORT')
ArrivingFlightsPerAirport.rename(columns={'ARRIVAL_DELAY':'Average Delay'}, inplace=True)

#getting additional data (airport names, airport position)
destination_data = df.groupby(['DESTINATION_AIRPORT'], as_index=False).agg({'DESTINATION_AIRPORT_NAME': 'first', 'DESTINATION_AIRPORT_LAT':'first', 'DESTINATION_AIRPORT_LON':'first'})
ArrivingFlightsPerAirport = ArrivingFlightsPerAirport.merge(destination_data, on='DESTINATION_AIRPORT')


addAirportsOrigin = allairports.groupby(['ORIGIN_AIRPORT']).nunique().reset_index()
addAirportsOrigin.drop(columns={'Unnamed: 0','DESTINATION_AIRPORT', 'ORIGIN_AIRPORT_NAME','DESTINATION_AIRPORT_NAME', 'ORIGIN_AIRPORT_LON', 'ORIGIN_AIRPORT_LAT', 'DESTINATION_AIRPORT_LON', 'DESTINATION_AIRPORT_LAT', 'ARRIVAL_DELAY'},inplace=True),
addOrigin_data = allairports.groupby(['ORIGIN_AIRPORT'], as_index=False).agg({'ORIGIN_AIRPORT_NAME': 'first', 'ORIGIN_AIRPORT_LAT':'first', 'ORIGIN_AIRPORT_LON':'first'})
addAirportsOrigin = addAirportsOrigin.merge(addOrigin_data, on='ORIGIN_AIRPORT')
#getting only airports that are not already in the ArrivingFlightsPerAirport dataframe as a destination
addAirportsOrigin = addAirportsOrigin[~addAirportsOrigin.ORIGIN_AIRPORT.isin(ArrivingFlightsPerAirport.DESTINATION_AIRPORT)]

addAirportsDestination = allairports.groupby(['DESTINATION_AIRPORT']).nunique().reset_index()
addAirportsDestination.drop(columns={'Unnamed: 0','ORIGIN_AIRPORT', 'ORIGIN_AIRPORT_NAME','DESTINATION_AIRPORT_NAME', 'ORIGIN_AIRPORT_LON', 'ORIGIN_AIRPORT_LAT', 'DESTINATION_AIRPORT_LON', 'DESTINATION_AIRPORT_LAT', 'ARRIVAL_DELAY'},inplace=True),
addDestination_data = allairports.groupby(['DESTINATION_AIRPORT'], as_index=False).agg({'DESTINATION_AIRPORT_NAME': 'first', 'DESTINATION_AIRPORT_LAT':'first', 'DESTINATION_AIRPORT_LON':'first'})
addAirportsDestination = addAirportsDestination.merge(addDestination_data, on='DESTINATION_AIRPORT')
#getting only airports that are not already in the ArrivingFlightsPerAirport dataframe as a destination
addAirportsDestination = addAirportsDestination[~addAirportsDestination.DESTINATION_AIRPORT.isin(ArrivingFlightsPerAirport.DESTINATION_AIRPORT)]


#printing min, max and mean of flightcount to help determine which method to use to normalize values
print('MIN:'+str(ArrivingFlightsPerAirport['flightcount'].min()))
print('MAX:'+str(ArrivingFlightsPerAirport['flightcount'].max()))
print('MEAN: '+str(ArrivingFlightsPerAirport['flightcount'].mean()))

#normalizing flightcount (necessary to size bubbles appropriately, so bubbles for large airports don't get too large while small airports are still visible)
normalized_flightcount= (ArrivingFlightsPerAirport['flightcount']-ArrivingFlightsPerAirport['flightcount'].min())/(ArrivingFlightsPerAirport['flightcount'].max()-ArrivingFlightsPerAirport['flightcount'].min()) #np.log(group_df['flightcount']) - logarithmic scaling not used bc/ min-max-scaling yields better results
ArrivingFlightsPerAirport['scaled flightcount'] = normalized_flightcount

#determining limits for sub-traces (grouping airports by flightcount reasonably)

'''
#testing same division in both directions (except that the positive one has more steps) with step ranges increasing in size moving from zero (using geometric series as general concept and only merging the steps closest to 0 into one)
limits = [(-20,-10), (-10,-5), (-5, -2.5), (-2.5, -1.25), (-1.25, 0), (0,1.25), (1.25, 2.5), (2.5,5), (5,10), (10,20), (20,40), (40,80)]
#tried using fibonacci sequence for scaling - didn't work out well (too many groups, some groups with very few airports):
limits = [(-20, -12.01),(-12, -7.01),(-7, -4.01),(-4, -2.01),(-2, -1.01),(-1,-0.01) ,(0,1), (1.01, 2), (2.01, 4), (4.01, 7), (7.01, 12), (12.01, 20), (20.01, 33), (33.01, 54), (54.01, 88) ]#(-20, 0),(0.01,20),(20.01,40),(40.01,60)]
'''
'''
#histogram to estimate sigma values for determining appropriate limits
figlimits = px.histogram(ArrivingFlightsPerAirport, x="Average Delay", hover_data=ArrivingFlightsPerAirport.columns)
figlimits.show()
'''

#limits determined by estimating sigma values (standard deviation) using the histogram
limits = [(-20, -5.01),(-5,10), (10.01,25), (25.01,60)]

colors = ['#16d446','#95a600','#c16d00','#cc1e1e'] # bright green: avg.delay -20 to -5 minutes (flights were early), dull green: avg. delay -5 to 10 minutes (a little early to reasonably delayed), orange: avg. delay 10 to 25 min (delayed), red: avg. delay 25-60 min (reaaaally late)
scale = 1500

fig = go.Figure()


for i in range(len(limits)):
    lim = limits[i]
    #creating sub groups based on flightcount
    df_sub = ArrivingFlightsPerAirport.loc[(ArrivingFlightsPerAirport['Average Delay'] >= lim[0]) & (ArrivingFlightsPerAirport['Average Delay'] <= lim[1])]
    
    #bubble map traces - destination airports.
    #multiple traces based on limits (grouping arrival delays)
    # hovertext shows airport name, no. of flights and the average arrival delay, marker size based on flightcount, color based on arrival delays,
    fig.add_trace(go.Scattergeo(
        locationmode = 'USA-states',
        lon = df_sub['DESTINATION_AIRPORT_LON'],
        lat = df_sub['DESTINATION_AIRPORT_LAT'],
        text = df_sub['DESTINATION_AIRPORT_NAME']+'<br>No. of Arriving Flights: '+df_sub['flightcount'].astype('str')+'<br>Average Arrival Delay: '+df_sub['Average Delay'].astype('str'),
        hovertemplate = '%{text}<extra></extra>',
        marker = dict(
            size = (df_sub['scaled flightcount'])*scale,
            sizemin = 3,#setting minimum size of dots so even airports with only 1 flight don't disappear on map
            color = colors[i],
            line_color=colors[i],
            line_width=0.5,
            sizemode = 'area'
        ),
        name = '{0} - {1}'.format(lim[0],lim[1])+' minutes delayed.'
    ))


#trace with origin airports that are not in destination airports already (without flightcount)
fig.add_trace(go.Scattergeo(
    locationmode = 'USA-states',
    lon = addAirportsOrigin['ORIGIN_AIRPORT_LON'],
    lat = addAirportsOrigin['ORIGIN_AIRPORT_LAT'],
    legendgroup = 'Airports with no Arriving Flights',
    name = 'Airports with no Arriving Flights',
    marker = dict(size = 3,color='grey'),
    text = addAirportsOrigin['ORIGIN_AIRPORT_NAME']+'<br>No. of Arriving Flights: 0',
    hovertemplate = '%{text}<extra></extra>',
    #showlegend = False
))
#trace with destination airports that are not in destination airports already (without flightcount)
fig.add_trace(go.Scattergeo(
    locationmode = 'USA-states',
    lon = addAirportsDestination['DESTINATION_AIRPORT_LON'],
    lat = addAirportsDestination['DESTINATION_AIRPORT_LAT'],
    legendgroup = 'Airports with no Arriving Flights',
    marker = dict(size = 3,color='grey'),
    text = addAirportsDestination['DESTINATION_AIRPORT_NAME']+'<br>No. of Arriving Flights: 0',
    hovertemplate = '%{text}<extra></extra>',
    showlegend = False
))


#i don't know what u want me to say... everything here is kind of obvious - setting the title, labeling the legend, setting the map scope and the color
fig.update_layout(
        title_text = 'Number Of Long Distance Flights and Average Arrival Delay of American Airports in 2015<br>(Click legend to toggle traces)',
        showlegend = True,
        legend_title_text = 'Average Arrival Delay in Minutes<br>Negative delays show by how many minutes flights were early.',
        geo = dict(
            scope = 'usa',
            landcolor = 'rgb(217, 217, 217)',
        )
    )

fig.write_html('out/HTML/Visual05-ScatterGeoMapBubble/Visual05-ScatterGeoMapBubble.html')
fig.show()