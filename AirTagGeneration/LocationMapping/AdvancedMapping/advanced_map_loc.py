import json
import pandas as pd
import folium
from folium.plugins import AntPath
from datetime import datetime

# just converting seconds to a more readable format lol
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

with open("data.json", "r") as file:
    data = json.load(file)

# this is mostly unchanged from your code
sorted_data = []
for device_id, positions in data.items():
    for pos in positions:
        sorted_data.append(pos)
sorted_data.sort(key=lambda x: x["decrypted_payload"]["timestamp"])

# instead of making a list we can use a dataframe to make it easier to work with
# pandas has a bit of a learning curve but it's worth it
df = pd.DataFrame([pos["decrypted_payload"] for pos in sorted_data])

df['datetime'] = pd.to_datetime(df['isodatetime'])
df['time_diff'] = df['datetime'].diff().dt.total_seconds()
average_time_diff = df['time_diff'][1:].mean()
time_diff_total = (df.iloc[-1]['datetime'] - df.iloc[0]['datetime']).total_seconds()

# we use the function we created here
formatted_total_time = format_time(time_diff_total)
formatted_avg_time = format_time(average_time_diff)

start_timestamp = df.iloc[0]['datetime'].strftime('%Y-%m-%d %H:%M:%S')
end_timestamp = df.iloc[-1]['datetime'].strftime('%Y-%m-%d %H:%M:%S')

# sanity check before plotting
if not df.empty:
    map_center = [df.iloc[0]['lat'], df.iloc[0]['lon']]
    m = folium.Map(location=map_center, zoom_start=13)

    # Plotting path, idk how I feel about the animation so might change
    latlon_pairs = list(zip(df['lat'], df['lon']))
    ant_path = AntPath(locations=latlon_pairs, dash_array=[10, 20], delay=1000, color='red', weight=5, pulse_color='black')
    m.add_child(ant_path)

    # Location markers look good, click to see timestamp
    for index, row in df.iterrows():
        folium.Marker([row['lat'], row['lon']], popup=f"Timestamp: {row['isodatetime']}", tooltip=f"Point {index+1}").add_to(m)

    # this is just some basic html to make a persistant title as
    # well as some useful(ish) info about the data points
    title_and_info_html = f'''
     <h3 align="center" style="font-size:20px; margin-top:10px;"><b>FindMy Flipper Location Mapper</b></h3>
     <div style="position: fixed; bottom: 50px; left: 50px; width: 300px; height: 150px; z-index:9999; font-size:14px; background-color: white; padding: 10px; border-radius: 10px; box-shadow: 0 0 5px rgba(0,0,0,0.5);">
     <b>Location Summary</b><br>
     Start: {start_timestamp}<br>
     End: {end_timestamp}<br>
     Total Time: {formatted_total_time}<br>
     Average Time Between Pings: {formatted_avg_time}<br>
     Created by Matthew KuKanich and luu176<br>
     </div>
     '''
    m.get_root().html.add_child(folium.Element(title_and_info_html))

    m.save('advanced_map.html')
    print("map info generated! Open 'advanced_map.html' in a web browser to view.")
else:
    print("No data available to plot.")
