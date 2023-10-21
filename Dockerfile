FROM python:3.9.10
WORKDIR /code
COPY requirements.txt .
RUN ["pip","install","-r","requirements.txt","-i","https://mirrors.aliyun.com/pypi/simple/"]
#RUN ["pip","install","nonebot-plugin-arcaea","-i","https://mirrors.aliyun.com/pypi/simple/"]
COPY . .
ENTRYPOINT ["python","bot.py"]
EXPOSE 10219