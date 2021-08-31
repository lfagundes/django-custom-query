FROM python:3
COPY ./requirements.txt /code/
RUN cd /code \
    && pip install -U pip \
    && pip install pytest-django ipython \
    && pip install -r requirements.txt

WORKDIR /code