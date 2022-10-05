FROM python:3.8

RUN mkdir /home/api

ADD src/requirements.txt /home/api/requirements.txt

RUN pip install --no-cache-dir -r /home/api/requirements.txt

ADD src/api /home/api/api

EXPOSE 8000

WORKDIR /home/api

ADD starter.py /home/api/starter.py

RUN python starter.py

CMD ["python", "-m", "uvicorn", "api.main:api", "--host", "0.0.0.0"]
