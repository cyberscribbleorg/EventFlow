# Use an official Superset base image
FROM apache/superset

USER root
RUN apt-get update && apt-get install -y postgresql-client
USER superset

# Set the working directory
WORKDIR /app

ENTRYPOINT ["/app/wait_for_it.sh", "postgres", "--", "/app/entry_point.sh"]

CMD ["superset", "run", "-p", "${SUPERSET_PORT}", "--with-threads", "-h", "0.0.0.0"]