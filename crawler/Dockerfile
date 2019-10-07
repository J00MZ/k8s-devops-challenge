FROM python:3.6-alpine

# Set the application directory
WORKDIR .

RUN apk add --no-cache gcc musl-dev libxslt-dev libmagic

ADD requirements.txt /crawler/requirements.txt
RUN pip3 install -r /crawler/requirements.txt

ADD . /crawler

ENTRYPOINT ["/crawler/main.py"]
CMD ["-h"]