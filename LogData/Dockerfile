FROM python:latest
LABEL Maintainer="nguyen.nguyen"
WORKDIR /usr/app/src
COPY ./ ./
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade google-api-python-client
CMD [ "python", "./test.py" ]