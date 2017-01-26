# Anaconda3 python distributionをベースContainerに利用
FROM continuumio/anaconda3
MAINTAINER kensuke-mi <kensuke.mit@gmail.com>

## apt-getで依存ライブラリのインストール
RUN apt-get update
RUN apt-get install -y software-properties-common --fix-missing
RUN apt-get update

### gccのインストール
RUN apt-get install -y gcc --fix-missing
RUN apt-get install -y g++ --fix-missing
RUN apt-get install -y swig2.0 --fix-missing
RUN apt-get install -y make --fix-missing
### mecabの辞書を先にutf-8でインストールしておく
RUN apt-get install -y mecab mecab-ipadic-utf8
RUN apt-get install -y mecab libmecab-dev
RUN apt-get install -y juman
RUN apt-get -y install pandoc
### DB郡のインストール
RUN apt-get install -y python-psycopg2 postgresql postgresql-contrib libpq-dev
RUN apt-get install -y sqlite3
RUN apt-get install -y vim wget
### apt-getでインストールすると、標準（と期待されている）の辞書パスと違う辞書パスになる。だからシンボリックリンクを作成
RUN ln -s /var/lib/mecab/dic/ /usr/lib/mecab/dic

## mecab neologdのインストール
WORKDIR /opt
RUN wget --no-check-certificate https://github.com/neologd/mecab-ipadic-neologd/tarball/master -O mecab-ipadic-neologd.tar
RUN tar -xvf mecab-ipadic-neologd.tar && rm mecab-ipadic-neologd.tar
RUN mv neologd-mecab-ipadic-neologd-* neologd-mecab-ipadic-neologd && cd neologd-mecab-ipadic-neologd && ( echo yes | ./bin/install-mecab-ipadic-neologd )
RUN echo "探偵ナイトスクープはおもしろい" | mecab -d /usr/lib/mecab/dic/mecab-ipadic-neologd/

## 手動でライブラリのインストール
RUN wget http://www.phontron.com/kytea/download/kytea-0.4.6.tar.gz
RUN tar -xzf kytea-0.4.6.tar.gz
WORKDIR /opt/kytea-0.4.6/
RUN ./configure && make  && make install
RUN export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

## Juman server起動
RUN juman -S

## Pythonパッケージのインストール
RUN conda install -y numpy scipy scikit-learn gensim cython

### コード配置用のディレクトリ
RUN mkdir /codes

### ローカルのコード郡を移動する
ADD sample_scripts /codes

### セットアップする
RUN pip install JapaneseTokenizer wikipedia sqlitedict DocumentFeatureSelection tqdm


CMD ["/bin/bash"]