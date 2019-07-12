FROM python:3.7-slim-stretch

# Copies Python sources
COPY ./src /
# Copies Requirements for pip
ADD requirements.txt /

# Installs pip required libraries
RUN pip install --requirement requirements.txt

# Runs bot
CMD [ "python", "-u", "./bot.py" ]