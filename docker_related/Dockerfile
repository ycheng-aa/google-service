FROM python:3.10
RUN mkdir /root/data
WORKDIR /root/data
RUN apt-get update && apt-get install -y vim mariadb-server lsb-release
COPY requirements/* ./
RUN pip3 install -r devel.txt
RUN echo 'set nu\nset hlsearch\nset syntax=on\nset autoindent\nset paste\n' >> /root/.vimrc
CMD service mariadb start
