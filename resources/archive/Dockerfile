# start by pulling the python image
FROM python:3.9

EXPOSE 80
EXPOSE 5000-6000
# switch working directory
WORKDIR /app

# copy every content from the local file to the image
COPY . /app

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["fuse.py" ]