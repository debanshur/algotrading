#install from requirements.txt
#run python script

FROM python:3.7
COPY requirements.txt /requirements.txt
COPY --chown=1000:1000 . /app
RUN pip install -r /requirements.txt
CMD python /app/supertrend_strategy.py