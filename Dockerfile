# pull official base image
FROM python:3.8-alpine

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup -S app && adduser -S app -G app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

# install dependencies
ENV PATH="${HOME}/.local/bin:${PATH}"
COPY --chown=app:app ./requirements.txt $HOME/requirements.txt
RUN pip install --user -r $HOME/requirements.txt

# copy project  (and entrypoint.sh inside them)
COPY --chown=app:app ./textmap $APP_HOME

# run entrypoint.sh
ENTRYPOINT ["/home/app/web/entrypoint.sh"]
