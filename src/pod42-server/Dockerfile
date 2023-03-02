# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install the function's dependencies using file requirements.txt
# from your project folder.

ENV PATH=$PATH:/root/.cargo/bin
RUN apt-get install -y gcc
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y

RUN  pip3 install --no-cache-dir -r requirements.txt

CMD [ "python", "./app.py" ]
