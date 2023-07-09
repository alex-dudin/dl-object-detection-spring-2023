FROM python:3.9.16-bullseye

COPY . /dl-object-detection-spring-2023

WORKDIR /dl-object-detection-spring-2023

RUN apt update \
 && apt install --no-install-recommends -y libgl1 \
 && pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

CMD streamlit run Home.py --browser.gatherUsageStats false
