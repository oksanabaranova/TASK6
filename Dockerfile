FROM python:3.8
ADD src /code
WORKDIR /code
EXPOSE 5000
EXPOSE 27017
RUN pip3 install -r requirements.txt
CMD python3 app.py
