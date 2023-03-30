FROM --platform=linux/amd64 python:3.8

# tell the port number the container should expose
EXPOSE 8080
ENV PORT 8080

RUN pip install -U pip

COPY requirements.txt app/requirements.txt
RUN pip install -r app/requirements.txt

# copy into a directory of its own (so it isn't in the toplevel dir)
COPY . /app
WORKDIR /app

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]