FROM elice/python-nginx:3.10

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "-g", "--"]

ENV VIRTUAL_ENV="/opt/python-env"
RUN python -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /elice-container/

COPY dist/*.tar.gz /tmp/app-release/

RUN set -ex; \
    export SDIST_TAR_FILENAME=$(find /tmp/app-release/ -type f -name "*.tar.gz"); \
    test $(echo $SDIST_TAR_FILENAME | wc -l) = "1"; \
    tar xvf $SDIST_TAR_FILENAME -C /tmp/app-release/; \
    mv ${SDIST_TAR_FILENAME%".tar.gz"}/* ./; \
    rm -r /tmp/app-release; \
    \
    pip install --no-cache-dir -U pip setuptools wheel; \
    pip install --no-cache-dir --no-deps -r requirements.txt; \
    \
    cp assets/nginx.conf /etc/nginx/nginx.conf

COPY docker-entry.sh  /

EXPOSE 80 443

CMD ["/bin/bash", "/docker-entry.sh"]
