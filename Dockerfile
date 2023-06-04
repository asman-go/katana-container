FROM projectdiscovery/katana

# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

WORKDIR /home/katana

COPY ./wrapper/* .

RUN python -m pip install -r requirements.txt

ENTRYPOINT [ "python", "-B", "main.py" ]