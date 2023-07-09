from typing import NamedTuple

import numpy as np
import streamlit as st

import folium
from streamlit_folium import st_folium

import storage
import ui


class MapObject(NamedTuple):
    name: str
    lat: float
    lon: float


def main():
    print('Map page update')

    st.set_page_config(page_title='Map - Rescue App')

    st.header('Места поиска')

    st.markdown("""
    На карте отмечена привязка загруженных изображений к местности.
    
    Зеленые маркеры используются для изображений, на которых были обнаружены люди.
    Синие маркеры используются для изображений без людей.
    """)

    lat_list = []
    lon_list = []
    markers_with_humans = []
    markers_without_humans = []
    for image in storage.Image.select():
        if image.latitude is None:
            continue

        tooltip = ''
        if image.timestamp is not None:
            tooltip = '<b>' + image.timestamp.strftime('%Y-%m-%d %H:%M') + '</b>'
        if image.upload.rescue_operation:
            if tooltip:
                tooltip += ' | '
            tooltip += f'<b>{image.upload.rescue_operation}</b>'
        tooltip += f'<br>{image.original_name}'

        if len(image.labels) > 0:
            icon = folium.Icon(color='green', icon='user', prefix='fa')
        else:
            icon = None

        marker = folium.Marker(
            location=[image.latitude, image.longitude],
            tooltip=tooltip, icon=icon)

        lat_list.append(image.latitude)
        lon_list.append(image.longitude)

        if len(image.labels) > 0:
            markers_with_humans.append(marker)
        else:
            markers_without_humans.append(marker)

    if not markers_with_humans and not markers_without_humans:
        st.write('Нет обработанных изображений с GPS-координатами.')
        return

    m = folium.Map(
        location=[np.mean(lat_list), np.mean(lon_list)],
        zoom_start=11, control_scale=True)

    m.fit_bounds([(np.min(lat_list), np.min(lon_list)), (np.max(lat_list), np.max(lon_list))])

    for marker in markers_without_humans:
        marker.add_to(m)

    for marker in markers_with_humans:
        marker.add_to(m)

    st_data = st_folium(m, use_container_width=True, returned_objects=['last_object_clicked'])

    last_object_clicked = st_data['last_object_clicked']
    if last_object_clicked is None:
        return

    latitude = last_object_clicked['lat']
    longitude = last_object_clicked['lng']

    image_info = storage.Image.get(storage.Image.longitude == longitude and storage.Image.latitude == latitude)
    ui.show_detection_results(image_info)


if __name__ == '__main__':
    main()
