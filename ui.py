import platform
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

import storage
import utils


def show_detection_results(image_info: storage.Image):
    image = Image.open(storage.IMAGES_DIR / image_info.path)

    patches = []
    for label in image_info.labels:
        patch_size = 200
        patch = image.crop((label.xc - patch_size / 2,
                            label.yc - patch_size / 2,
                            label.xc + patch_size / 2,
                            label.yc + patch_size / 2))

        draw = ImageDraw.Draw(patch, 'RGBA')

        if platform.system() == 'Windows':
            font = ImageFont.truetype('arial.ttf', 15)
        else:
            font = ImageFont.truetype('DejaVuSans.ttf', 15)

        text = f'{label.confidence:.2f}'
        bbox = draw.textbbox((patch_size - 3, patch_size - 3), text, font=font, anchor='rb')
        draw.rectangle((bbox[0] - 3, bbox[1] - 3, bbox[2] + 3, bbox[3] + 3), fill=(30,30,30,125))
        draw.text((patch_size - 3, patch_size - 3), text, fill=(255,255,255), font=font, anchor='rb')

        patches.append(patch)

    draw = ImageDraw.Draw(image)
    for label in image_info.labels:
        draw.rectangle(((label.xmin, label.ymin), (label.xmax, label.ymax)), width=3, outline='red')

    st.subheader(image_info.original_name)

    if image_info.latitude is not None:
        lat_dms = utils.deg_to_dms(image_info.latitude, 'lat')
        lon_dms = utils.deg_to_dms(image_info.longitude, 'lon')
        st.write(f'Координаты: [{lat_dms} {lon_dms}](https://www.google.com/maps/place/{image_info.latitude},{image_info.longitude})')

    st.image(image)

    if len(image_info.labels) == 0:
        st.write('Люди не обнаружены')
    else:
        st.write(f'Обнаружено людей: {len(image_info.labels)}')
        columns = st.columns(3)
        for i, (label, patch) in enumerate(zip(image_info.labels, patches)):
            with columns[i % 3]:
                st.image(patch)
