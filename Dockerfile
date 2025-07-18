FROM python:3.11
WORKDIR /powercoachapp

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY powercoachapp/ .

EXPOSE 10000
CMD ["python", "run.py"]