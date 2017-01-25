# Requirement

- Python >= 3.5 (Anaconda3の利用がオススメ)
- Mecab
    - Neologd辞書のインストール

# セットアップ

## 形態素解析機のインストール

### Mecab

ここに書く

## 依存ライブラリのインストール

```
python setup.py install
```

### (ヒント) エラー回避のため、anacondaディストリビューションを利用する場合

先にエラーが発生しやすいパッケージをインストールしておきます。

```
conda install numpy scipy scikit-learn cython
```

## wikipediaテキストデータの取得

サンプルテキストとしてwikipediaのテキストを取得します。

`./sample_scripts` に移動し

```
python ./get_wikipedia_text.py
```

`sample_scripts/wikipedia_data` に２種類のJsonファイルが配置されます。


# サンプルコード

以下はすべて `./sample_scripts` に居るものとします。

## 形態素解析

形態素分割を実行するためのサンプルコード、単語集計を実行するためのサンプルコードを保存しています。

`python sample_tokenization.py`

## キーワード抽出 & カテゴリ分類モデル構築

カテゴリラベル情報を利用して、カテゴリごとのキーワード抽出、ついでにカテゴリ分類モデルの構築を実施します。

`python sample_keyword.py`

## カテゴリ分類

構築したモデルを使ってカテゴリ分類を実施します。
モデルの評価をAccuracyで実施します。

`python sample_category_classification.py`