# Use an official Superset base image
FROM apache/superset

USER root
RUN apt-get update && apt-get install -y postgresql-client


COPY . /app
RUN chmod +x /app/wait_for_it.sh
RUN chmod +x /app/entry_point.sh

ENTRYPOINT ["/app/wait_for_it.sh", "postgres", "--", "/app/entry_point.sh"]

USER superset