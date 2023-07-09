import streamlit as st


def main():
    st.set_page_config(page_title='About - Rescue App')

    st.header('Информация о приложении')

    st.markdown("""
    Данное web-приложение было разработано в качестве итогового проекта на курсе
    "Deep Learning (семестр 1, весна 2023): продвинутый поток" (https://stepik.org/course/135003).

    Основными источниками вдохновения для выбора темы разработки были соревнования:
    - Технологический конкурс НТИ Up Great «Экстренный поиск» (https://ods.ai/competitions/rescue-upgreat-one)
    - 1st Lacmus Computer Vision Competition (https://ods.ai/competitions/lacmus-cvc-soc2021)
    - Детекция человеческих силуэтов на снимках лесного массива, полученных с помощью БПЛА (https://2022.hacks-ai.ru/championships/758299)

    Примеры фотоснимков с БПЛА взяты из базы данных HERIDAL: http://ipsar.fesb.unist.hr/HERIDAL%20database.html

    Интерфейс приложения создан с помощью библиотеки Streamlit (https://streamlit.io/).
    Использовались дополнительные компоненты:
    - streamlit-folium (https://github.com/randyzwitch/streamlit-folium) для отображения интерактивной карты
    - streamlit-aggrid (https://github.com/PablocFonseca/streamlit-aggrid) для отображения интерактивных таблиц

    Для детектирования людей на изображениях использовалась модель YOLO8 (https://github.com/ultralytics/ultralytics).

    Хранилище данных организовано на основе Sqlite и ORM Peewee (https://github.com/coleifer/peewee).
    """)


if __name__ == '__main__':
    main()
