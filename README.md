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

`python sample_tokenization.py`


