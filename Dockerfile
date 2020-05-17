# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.7-slim



# Install production dependencies.
RUN pip install google-api-python-client google-cloud-firestore grpcio
RUN pip install Flask flask_api numpy gunicorn 


# Copy local code to the container image.
ENV GOOGLE_AUTH_URL ""
ENV GOOGLE_PROJECT_ID ""
ENV GOOGLE_SERVICE_ACCOUNT_SECRETS ""
ENV GOOGLE_SERVICE_ACCOUNT ""
ENV GOOGLE_REGION ""
ENV GOOGLE_IMAGE ""
ENV GOOGLE_EMAIL ""

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./


# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app

