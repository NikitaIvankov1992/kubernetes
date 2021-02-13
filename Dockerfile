# set base image
FROM python:3.8-slim

# set the working directory in the container
WORKDIR /app

# copy the dependencies file to the working directory
COPY . .

# update packet-manager
RUN apt update

# install dependencies
RUN pip3 install -r requirements.txt

# command to run on container start
ENTRYPOINT [ "python3", "./checker.py" ]
