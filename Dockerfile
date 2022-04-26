FROM ubuntu:20.04 as base 
USER root

## Setting default environment variables
ENV WEB_ROOT=/web_root
ENV APP_ROOT=${WEB_ROOT}/dev_arches
# Root project folder
ENV ARCHES_ROOT=${WEB_ROOT}/arches
ENV WHEELS=/wheels
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y make software-properties-common

# Get the pre-built python wheels from the build environment
RUN mkdir ${WEB_ROOT}

# Install packages required to run Arches
# Note that the ubuntu/debian package for libgdal1-dev pulls in libgdal1i, which is built
# with everything enabled, and so, it has a huge amount of dependancies (everything that GDAL
# support, directly and indirectly pulling in mysql-common, odbc, jp2, perl! ... )
# a minimised build of GDAL could remove several hundred MB from the container layer.
RUN set -ex \
  && RUN_DEPS=" \
  build-essential \
  python3.8-dev \
  mime-support \
  libgdal-dev \
  python3-venv \
  postgresql-client-12 \
  python3.8 \
  python3.8-distutils \
  python3.8-venv \
  dos2unix \
  " \
  && apt-get install -y --no-install-recommends curl \
  && curl -sL https://deb.nodesource.com/setup_14.x | bash - \
  && curl -sL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
  && add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -sc)-pgdg main" \
  && apt-get update -y \
  && apt-get install -y --no-install-recommends $RUN_DEPS \
  && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
  && python3.8 get-pip.py \
  && apt-get install -y nodejs \
  && npm install -g yarn \
  && apt-get -y install git\
  && apt-get install -y wget



WORKDIR ${ARCHES_ROOT}
#Clone v6 arches
RUN git clone -b docker --single-branch https://github.com/KacperSzyf/arches.git .

# Install Yarn components
RUN yarn install

# install cloned arches repo as a pip package
RUN pip install -e . --no-use-pep517 && pip install -r arches/install/requirements_dev.txt

RUN mkdir /var/log/supervisor
RUN mkdir /var/log/celery

# Set default workdir
WORKDIR ${WEB_ROOT}
#Temporary, override current v6 entry point with Arches HER entry point
RUN cp ${ARCHES_ROOT}/docker/entrypoint.sh .
RUN chmod -R 700 ${WEB_ROOT}/entrypoint.sh &&\
  dos2unix ${WEB_ROOT}/entrypoint.sh

RUN rm -rf /root/.cache/pip/*

# # Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]
CMD ["init_arches"]

# Expose port 8000
EXPOSE 8000