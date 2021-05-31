FROM postgres
ENV POSTGRES_PASSWORD visto
ENV POSTGRES_DB world
COPY world.sql /docker-entrypoint-initdb.d/