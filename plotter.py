import pandas as pd
import folium
from folium import GeoJson
import loader
import common

all_paths_df, bike_paths_df, pedestrian_paths_df, street_lights_df = loader.load_data()

lights_close_to_path_df = pd.read_csv(common.lights_close_to_paths_data, index_col=None, header=None,
                                      names=["index", "light_latitude", "light_longitude", "close_to_path",
                                             "distance_to_path", "pathA_latitude", "pathA_longitude", "pathB_latitude",
                                             "pathB_longitude", "path_segment_length", "path_segment_ID"])

paths_close_to_light = pd.read_csv(common.paths_close_to_light_data, index_col=None, header=0,
                                   names=["index", "pointA_latitude", "pointA_longitude", "pointB_latitude",
                                          "pointB_longitude", "path_segment_ID", "sub_segment_length"])

paths_not_close_to_light = pd.read_csv(common.paths_not_close_to_light_data, index_col=None, header=0,
                                       names=["index", "pointA_latitude", "pointA_longitude", "pointB_latitude",
                                              "pointB_longitude", "path_segment_ID", "sub_segment_length"])

# Add 'the_geom' dicts to these dataframes, for plotting with folium. Very hacky.
# Can't do it in the jupyter notebook because csv converts the json column to non-json. Ugh.
tmp_list = []
for _idx, bike_path_entry in paths_close_to_light.iterrows():
    tmp_list.append(
        [{
            "type": "MultiLineString",
            "coordinates": [
                [
                    [bike_path_entry["pointA_longitude"],
                        bike_path_entry["pointA_latitude"]],
                    [bike_path_entry["pointB_longitude"],
                        bike_path_entry["pointB_latitude"]]
                ]
            ]
        }
        ])
paths_close_to_light['the_geom'] = pd.DataFrame(tmp_list)

# Add 'the_geom' dicts to these dataframes, for plotting with folium. Very hacky.
# Can't do it in the jupyter notebook because csv converts the json column to non-json. Ugh.
tmp_list = []
for _idx, bike_path_entry in paths_not_close_to_light.iterrows():
    tmp_list.append(
        [{
            "type": "MultiLineString",
            "coordinates": [
                [
                    [bike_path_entry["pointA_longitude"],
                        bike_path_entry["pointA_latitude"]],
                    [bike_path_entry["pointB_longitude"],
                        bike_path_entry["pointB_latitude"]]
                ]
            ]
        }
        ])
paths_not_close_to_light['the_geom'] = pd.DataFrame(tmp_list)

# coordinates from Canberra wiki
initial_lat = -35.473469
initial_lng = 149.012375

# Load map centred on average coordinates
my_map = folium.Map(location=[initial_lat, initial_lng],
                    zoom_start=10, tiles="cartodbpositron")

# Style definitions
bike_path_style = {'color': '#228B22', 'fillOpacity': 0.5}
bike_path_not_close_to_lights_style = {'color': '#d63a3a', 'fillOpacity': 0.5}
pedestrian_path_style = {'color': '#86bd86', 'fillOpacity': 0.5}

# Bike paths
bike_group = folium.FeatureGroup("Bike Paths")
for _idx, bike_path_entry in bike_paths_df.iterrows():
    bike_group.add_child(
        GeoJson(
            data=bike_path_entry['the_geom'],
            name='bike_path',
            style_function=lambda x: bike_path_style
        )
    )
my_map.add_child(bike_group)
bike_group.add_to(my_map)

# Bike paths NOT close to lights (keep on top)
bike_not_lights_group = folium.FeatureGroup("Bike Paths Not Near Lights")

for _idx, bike_path_entry in paths_not_close_to_light.iterrows():
    bike_not_lights_group.add_child(
        GeoJson(
            data=bike_path_entry['the_geom'],
            name='bike_path',
            style_function=lambda x: bike_path_not_close_to_lights_style
        )
    )
my_map.add_child(bike_not_lights_group)
bike_not_lights_group.add_to(my_map)

# Bike paths close to lights (keep on top)
bike_lights_group = folium.FeatureGroup("Bike Paths Near Lights")
for _idx, bike_path_entry in paths_close_to_light.iterrows():
    bike_lights_group.add_child(
        GeoJson(
            data=bike_path_entry['the_geom'],
            name='bike_path',
            style_function=lambda x: bike_path_style
        )
    )
my_map.add_child(bike_lights_group)
bike_lights_group.add_to(my_map)

# Pedestrian paths
pedestrian_group = folium.FeatureGroup("Pedestrian Paths")
for _idx, pedestrian_path_entry in pedestrian_paths_df.iterrows():
    pedestrian_group.add_child(
        GeoJson(
            data=pedestrian_path_entry['the_geom'],
            name='pedestrian_path',
            style_function=lambda x: pedestrian_path_style
        )
    )
my_map.add_child(pedestrian_group)
pedestrian_group.add_to(my_map)

# Street Lights Close to Bike Paths
light_group = folium.FeatureGroup("Street Lights")
for _idx, street_light_entry in lights_close_to_path_df.iterrows():
    light_group.add_child(
        folium.CircleMarker(
            location=[float(street_light_entry['light_latitude']), float(
                street_light_entry['light_longitude'])],
            radius=0.2,  # 0.2
            color="yellow",
            fill=True,
            fill_color="yellow",
            fill_opacity=0.6
        )
    )
my_map.add_child(light_group)
light_group.add_to(my_map)


my_map.keep_in_front(bike_lights_group, bike_not_lights_group)
my_map.add_child(folium.LayerControl())

my_map.save(common.output_map)
