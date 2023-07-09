import datetime as dt
import io

import streamlit as st
from PIL import Image

import settings
import storage
import ui
import utils


@st.cache_resource(show_spinner='Загрузка модели YOLO8...')
def get_model():
    print('Load YOLO model...')

    import ultralytics
    ultralytics.hub.utils.events.enabled = False  # disable telemetry
    
    model = ultralytics.YOLO('yolov8x.pt')
    print('Model successfully loaded')
    return model


def show_results():
    if 'upload_id' not in st.session_state:
        return

    upload_id = st.session_state['upload_id']
    upload_info = storage.Upload.get(storage.Upload.id == upload_id)

    human_count = sum(len(image_info.labels) for image_info in upload_info.images)
    if human_count > 0:
        st.success('Обнаружены люди!')
    else:
        st.info('Люди не обнаружены')

    for image_info in upload_info.images:
        ui.show_detection_results(image_info)


def main():
    print('Detect page update')

    st.set_page_config(page_title='Detect - Rescue App')

    st.header('Поиск людей на изображениях')

    st.write('Укажите название поисково-спасательной операции и загрузите одно или несколько изображений на которых необходимо обнаружить людей.')

    rescue_operation = st.text_input(
        'Поисково-спасательная операция:',
        value='Тест', max_chars=100)

    with st.form("upload-form", clear_on_submit=True):
        uploaded_files = st.file_uploader(
            'Изображения с БПЛА:',
            type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        submitted = st.form_submit_button('Обработать изображения')

    if not submitted:
        #show_results()
        return

    if not uploaded_files:
        return

    if 'upload_id' in st.session_state:
        del st.session_state['upload_id']

    model = get_model()

    upload_info = storage.Upload.create(
        timestamp=dt.datetime.now(),
        rescue_operation=rescue_operation)

    progress_bar = st.progress(0)

    with st.spinner('Обработка изображений...'):
        for i, uploaded_file in enumerate(uploaded_files):
            print('Process file:', uploaded_file.name)
            bytes_data = uploaded_file.getvalue()

            image = Image.open(io.BytesIO(bytes_data))
            latitude, longitude = utils.get_gps_coordinates(image)

            image_path = storage.upload_image(bytes_data, uploaded_file.name)
            image_info = storage.Image.create(
                upload=upload_info,
                timestamp=utils.get_datetime_original(image),
                path=image_path.as_posix(),
                original_name=uploaded_file.name,
                longitude=longitude,
                latitude=latitude)

            image_width = image.size[0]
            image_height = image.size[1]

            results = model.predict(source=image, conf=settings.YOLO8_CONF_THRESHOLD,
                                    iou=settings.YOLO8_IOU_THRESHOLD, imgsz=settings.YOLO8_IMAGE_SIZE,
                                    device=settings.YOLO8_DEVICE, classes=0, verbose=False)
            for result in results:
                for ((xc, yc, w, h), conf) in zip(result.boxes.xywhn.tolist(), result.boxes.conf.tolist()):
                    print(f'Detected: box=[{xc:.4f}, {yc:.4f}, {w:.4f}, {h:.4f}] conf={conf:.4f}')
                    xmin = (xc - w/2) * image_width
                    xmax = (xc + w/2) * image_width
                    ymin = (yc - h/2) * image_height
                    ymax = (yc + h/2) * image_height
                    storage.Label.create(image=image_info, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, confidence=conf)

            progress_bar.progress((i + 1) / len(uploaded_files))

    st.session_state['upload_id'] = upload_info.id
    show_results()


if __name__ == '__main__':
    main()
