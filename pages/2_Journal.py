import datetime as dt
from typing import NamedTuple, Optional

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode

import storage
import ui


class ImageInfo(NamedTuple):
    image_id: int
    rescue_operation: str
    timestamp: dt.datetime
    name: str
    latitude: Optional[float]
    longitude: Optional[float]
    detected: int


def main():
    print('Journal page update')

    st.set_page_config(page_title='Journal - Rescue App')

    st.header('Журнал поиска')

    st.markdown("""
    В журнале можно посмотреть все загруженные изображения и результаты их обработки.
    """)

    items = []
    for image in storage.Image.select():
        items.append(ImageInfo(
            image.id,
            image.upload.rescue_operation,
            image.timestamp,
            image.original_name,
            image.latitude,
            image.longitude,
            len(image.labels)))

    if not items:
        st.write('Нет обработанных изображений.')
        return

    data = pd.DataFrame(items)

    grid_options = {
        'defaultColDef': {
            'minWidth': 5,
            'editable': False,
            'filter': True,
            'resizable': True,
            'sortable': True,
            'enableRowGroup': False,
            'value': True,
            'aggFunc': 'sum',
        },
        'columnDefs': [
            {
                'headerName': 'Операция',
                'field': 'rescue_operation',
            },
            {
                'headerName': 'Дата и время',
                'field': 'timestamp',
                'type': ['dateColumnFilter', 'customDateTimeFormat'],
                'custom_format_string': 'yyyy-MM-dd hh:mm',
            },
            {
                'headerName': 'Имя файла',
                'field': 'name',
            },
            {
                'headerName': 'Широта',
                'field': 'latitude',
                'type': ['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
                'precision': 5,
            },
            {
                'headerName': 'Долгота',
                'field': 'latitude',
                'type': ['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
                'precision': 5,
            },
            {
                'headerName': 'Обнаружено',
                'field': 'detected',
                'type': ['numericColumn', 'numberColumnFilter'],
            }
        ],
        'rowSelection': 'single',
        'rowMultiSelectWithClick': False,
        'suppressRowDeselection': True,
    }

    response = AgGrid(
        data,
        gridOptions=grid_options,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        height=500)

    selected = response['selected_rows']
    if selected:
        image_id = selected[0]['image_id']
        image_info = storage.Image.get(storage.Image.id == image_id)
        ui.show_detection_results(image_info)


if __name__ == '__main__':
    main()
