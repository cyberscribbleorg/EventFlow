# Use an official Superset base image
FROM apache/superset

USER root
RUN apt-get update && apt-get install -y postgresql-client


COPY wait_for_it.sh /app/wait_for_it.sh
RUN chmod +x /app/wait_for_it.sh
COPY entry_point.sh /app/entry_point.sh
RUN chmod +x /app/entry_point.sh

ENTRYPOINT ["/app/wait_for_it.sh", "postgres", "--", "/app/entry_point.sh"]
USER superset
CMD ["superset", "run", "-p", "${SUPERSET_PORT}", "--with-threads", "-h", "0.0.0.0"]