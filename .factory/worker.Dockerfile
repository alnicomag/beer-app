# ソフトウェアファクトリーのワーカーが、このリポジトリの作業に使うイメージ。
# ファクトリーの基本イメージ(Node、git、Claude Code)に、factory.yml の commands が
# 使うツールを足す。
#
# 作り方(ファクトリーのホストで、このリポジトリの main の内容から作る):
#   docker build -f .factory/worker.Dockerfile \
#     --build-arg FACTORY_BASE_IMAGE=<ファクトリーの基本イメージ> \
#     -t <このリポジトリ用のイメージ名> .factory
#
# ワーカーのコンテナは、ルートが読み取り専用で、書けるのは作業場所(HOME を含む)と
# /tmp だけである。実行時に入れるものを残さず、必要なものはここで入れる。

# 基本イメージの名前は、ファクトリーが決めて渡す。
ARG FACTORY_BASE_IMAGE
FROM ${FACTORY_BASE_IMAGE}

USER root

# opencv-python の読み込みに要る共有ライブラリ。
RUN apt-get update \
  && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

# uv。版を固定する。
COPY --from=ghcr.io/astral-sh/uv:0.9.11 /uv /uvx /usr/local/bin/

# Python はイメージに入れ、実行時にはダウンロードしない。
# 版は pyproject.toml の requires-python に合わせる。
ENV UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy
RUN UV_PYTHON_DOWNLOADS=automatic uv python install 3.13 \
  && chmod -R a+rX /opt/uv-python

# 基本イメージと同じ、権限のないユーザーに戻す。
USER node
