FROM python:3.7-slim-stretch

# Copies Requirements for pip
COPY requirements.txt /
# Installs pip required libraries
RUN pip install --requirement requirements.txt

# Copies Python sources
COPY ./src /

# Runs bot
ENTRYPOINT ["python", "-u", "./twitter_bot.py"]
