# pull official base image
FROM python:3.8-alpine

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip

# create directory for the app user
RUN mkdir -p /home/nonroot

# create the app user
RUN addgroup -S nonroot && adduser -S nonroot -G nonroot

# create the appropriate directories
ENV HOME=/home/nonroot
ENV APP_HOME=/home/nonroot/textmap
RUN mkdir $APP_HOME
# only stub to correspond with non docker development environment
RUN mkdir -p /var/www/textmap/static/
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles
WORKDIR $APP_HOME

# chown all the files to the app user
RUN chown -R nonroot:nonroot $APP_HOME

# change to the app user
USER nonroot

# install dependencies
ENV PATH="${HOME}/.local/bin:${PATH}"
COPY --chown=nonroot:nonroot ./requirements.txt $HOME/requirements.txt
RUN pip install --user -r $HOME/requirements.txt

# copy project  (and entrypoint.sh inside them)
COPY --chown=nonroot:nonroot ./textmap $APP_HOME

# run entrypoint.sh
ENTRYPOINT ["/home/nonroot/textmap/entrypoint.sh"]
