FROM python:3.11

#Installing the libGL.so.1 package, which is a dependency of OpenCV. Usualy a system package, but not for Docker servers.
RUN apt-get update && apt-get install -y libgl1 && rm -rf /var/lib/apt/lists/*

WORKDIR /powercoach

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Only add the files you want to add:
COPY powercoachapp/ powercoachapp/

EXPOSE 10000
CMD ["python3", "-m", "powercoachapp.run"]