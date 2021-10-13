import pandas as pd
from sodapy import Socrata


def get_data_from_client():

    try:
        import secrets
        client = Socrata("www.data.act.gov.au",
                         app_token=secrets.app_token,
                         username=secrets.username,
                         password=secrets.password)

    except ModuleNotFoundError:
        client = Socrata("www.data.act.gov.au", None)

    street_light_dataset = client.get("n9u5-bt96", limit=100000)
    paths_dataset = client.get("ee7d-h7nm", limit=100000)

    return paths_dataset, street_light_dataset


def load_data():

    all_paths_dataset, street_light_dataset = get_data_from_client()
    all_paths_df = pd.DataFrame.from_records(all_paths_dataset)
    street_lights_df = pd.DataFrame.from_records(street_light_dataset)

    bike_paths_df = all_paths_df[all_paths_df['path_type'] == 'CYCLEPATH']
    pedestrian_paths_df = all_paths_df[all_paths_df['path_type'] == 'FOOTPATH']

    return all_paths_df, bike_paths_df, pedestrian_paths_df, street_lights_df
