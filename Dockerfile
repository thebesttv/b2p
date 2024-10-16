FROM ubuntu:22.04

# 设置环境变量以非交互方式安装 tzdata 并设置时区为 Asia/Shanghai
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y \
    wget curl tzdata \
    python3 \
    python3-pip \
    php \
    && apt-get clean

RUN pip3 install --no-cache-dir tqdm pyyaml

# 安装 ffmpeg
RUN cd /tmp && \
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    tar xvf ffmpeg-release-amd64-static.tar.xz && \
    mv ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/ffmpeg && \
    mv ffmpeg-*-amd64-static/ffprobe /usr/local/bin/ffprobe && \
    rm -rf ffmpeg-release-amd64-static.tar.xz ffmpeg-*-amd64-static

# 安装 .NET SDK 8.0 和 BBDown
RUN apt-get install -y dotnet-sdk-8.0 && \
    dotnet tool install --global BBDown

ENV PATH="${PATH}:/root/.dotnet/tools"

# 显示版本信息
RUN ffmpeg -version | head -n1 && \
    echo && \
    BBDown --help --version
