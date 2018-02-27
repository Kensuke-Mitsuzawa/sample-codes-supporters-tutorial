from JapaneseTokenizer import MecabWrapper
from DocumentFeatureSelection import interface
from DocumentFeatureSelection.models import PersistentDict
from typing import List, Tuple, Dict, Union, Any
from sqlitedict import SqliteDict
import json
import logging
import nltk
import tempfile
import os
logger = logging.getLogger()
logger.setLevel(10)

SLEEP_TIME = 2

"""ラベルを利用した特徴量抽出を実施します。
Python3.5.1の環境下で動作を確認しています。
"""

__author__ = "Kensuke Mitsuzawa"
__author_email__ = "kensuke.mit@gmail.com"
__license_name__ = "MIT"


def tokenize_text(input_text:str,
                  tokenizer_obj:MecabWrapper,
                  pos_condition:List[Tuple[str,...]])->List[str]:
    """* What you can do
    - １文書に対して、形態素分割を実施する
    """
    ### 形態素分割;tokenize() -> 品詞フィルタリング;filter() -> List[str]に変換;convert_list_object()
    return tokenizer_obj.tokenize(input_text).filter(pos_condition=pos_condition).convert_list_object()
    ### 原型(辞書系)に変換せず、活用された状態のまま、欲しい場合は is_surface=True のフラグを与える
    #return tokenizer_obj.tokenize(input_text, is_surface=True).filter(pos_condition=pos_condition).convert_list_object()


def construct_cached_dict(tokenizer_obj:MecabWrapper,
                          seq_text_data:List[Dict[str,Any]],
                          pos_condition:List[Tuple[str,...]],
                          engine:str='PersistentDict')->Union[PersistentDict, SqliteDict]:
    """* What you can do
    - wikipediaテキスト形態素分割して、DocumentFeatureSelectionの入力フォーマットを整えます。
    - dictと互換性のあるクラスを使って、ディクス上にデータを展開します。
    - Pythonのdictは巨大データ(1G~, 2G~)が苦手です。巨大データを扱う場合はdictでメモリ上に展開するのでなく、ディスク上に展開しましょう。

    * Output
    - DocumentFeatureSelectionの入力は
        - {'ラベル名': [ [特徴量] ]} となっています。
        >>> {'映画': [ ['スターウォーズ', 'おもしろい'], ['インディ・ジョーンズ', 'クソワロ'] ]}

    * Tips
    - 今回は、if __name__ == '__main__': で json -> dict しているので、この時点でデータの大部分がメモリ上に展開されてしまっています。
    - なので、この関数は「サンプル」ということで、今回のケースではそれほど、大きな意味はありません。
    - DBからfetchするときなど、一気にfetchせずに、generatorオブジェクトを使いながら、DB -> cached dictの手順でメモリに載せるデータを少なくすると効果的です。
    """
    """sqliteDictはsqliteベースのキャッシュdict, PersistentDictはjsonベースのキャッシュdict
    sqliteDictの方が定期的にメンテナンスされていますが、PersistentDictの方が速度が早いです。"""
    ### tempfile.mkdtemp()はシステム一時ディレクトリ（たいていは/var/tmp/以下のどこか）を作ってくれます。
    ### システムが定期的にディレクトリごと削除してくれるので、一時ファイル生成に適しています。
    path_cached_dict = os.path.join(tempfile.mkdtemp(), 'cached_dict')
    if engine == 'PersistentDict':
        cached_dict = PersistentDict(filename=path_cached_dict)
    else:
        cached_dict = SqliteDict(filename=path_cached_dict, autocommit=Tuple)

    for wiki_document_obj in seq_text_data:
        seq_tokens_wiki_document = tokenize_text(input_text=wiki_document_obj['text'],tokenizer_obj=tokenizer_obj, pos_condition=pos_condition)
        label_name = wiki_document_obj['gold_label']

        if label_name not in cached_dict:
            cached_dict[label_name] = [seq_tokens_wiki_document]
        else:
            cached_dict[label_name].append(seq_tokens_wiki_document)

    if isinstance(cached_dict, SqliteDict):
        cached_dict.close()

    ### printを実行してみると、cache dictが通常のdictと同じインターフェースを持っていることが確認できます。
    #print(cached_dict)
    return cached_dict


def construct_ngram_cached_dict(tokenizer_obj:MecabWrapper,
                                seq_text_data:List[Dict[str,Any]],
                                pos_condition:List[Tuple[str,...]],
                                n_value:int=2,
                                engine:str='PersistentDict')->Union[PersistentDict, SqliteDict]:
    """* What you can do
    - 基本的にconstruct_cached_dict()と同じです。
    - 単語でなく、「フレーズ」で入力データを作成します。
        - フレーズに拡張すると、「単語」では失われていた意味が見える・・・可能性があります。
    """
    path_cached_dict = os.path.join(tempfile.mkdtemp(), 'cached_dict')
    if engine == 'PersistentDict':
        cached_dict = PersistentDict(filename=path_cached_dict)
    else:
        cached_dict = SqliteDict(filename=path_cached_dict, autocommit=Tuple)

    for wiki_document_obj in seq_text_data:
        seq_tokens_wiki_document = tokenize_text(input_text=wiki_document_obj['text'],tokenizer_obj=tokenizer_obj, pos_condition=pos_condition)
        ### n-gramの作成 ###
        seq_ngram_wiki_document = list(nltk.ngrams(sequence=seq_tokens_wiki_document, n=n_value))
        label_name = wiki_document_obj['gold_label']

        if label_name not in cached_dict:
            cached_dict[label_name] = [seq_ngram_wiki_document]
        else:
            cached_dict[label_name].append(seq_ngram_wiki_document)

    if isinstance(cached_dict, SqliteDict):
        cached_dict.close()

    ### printを実行してみると、cache dictが通常のdictと同じインターフェースを持っていることが確認できます。
    #print(cached_dict)
    return cached_dict


def run_feature_selection(tokenized_documents:Union[SqliteDict, PersistentDict],
                          selection_method:str='soa'):
    """* What you can do
    - 特徴量抽出を実行します。
    - 個人的には'soa'が一番オススメです。
        - ラベルごとに重みスコアを出力します。
        - マイナス∞ から プラス∞の値を取ります。
        - マイナスは「ラベルと関係性が低い」、プラスは「ラベルと関係が深い」と解釈できます。
        - [注意] soaでは、「すべてのラベルに共通した単語」しか重み付けをすることができません。いずれかのラベルで頻度が0の場合、その単語重みは0になります。
    """
    score_result_obj = interface.run_feature_selection(input_dict=tokenized_documents,
                                                       method=selection_method,
                                                       use_cython=True,  # 計算にcythonを利用する可否。cythonを使うと50倍~200倍近く早くなります。
                                                       is_use_cache=True,  # データが大規模すぎる場合にTrueにします。中間データをメモリでなくディスクに載せます
                                                       is_use_memmap=True  # データが大規模すぎる場合にTrueにします。中間データをメモリでなくディスクに載せます
                                                       )
    assert isinstance(score_result_obj, interface.ScoredResultObject)
    """戻り値はinterface.ScoredResultObject, 計算の過程で利用したmatrixオブジェクトなどが格納されています。"""
    # 重み行列が必要な人はアトリビュートにアクセスすると内容を取得できます。
    #print(score_result_obj.scored_matrix)  # 重み行列(scipy.sparse.csr_matrix)
    # 重み行列とか興味ない人はScoreMatrix2ScoreDictionary()メソッドを実行します。
    # レコード状のタプルオブジェクトが、重みが大きい順にソートされて、返却されます。
    seq_score_dict = score_result_obj.ScoreMatrix2ScoreDictionary()
    print(seq_score_dict[:5])

    return seq_score_dict


def main(tokenizer_obj:MecabWrapper,
         seq_text_data:List[Dict[str,Any]],
         pos_condition:List[Tuple[str,...]]):
    # ------------------------------------------------------------------------
    # 単語で特徴量抽出の場合
    cached_dict = construct_cached_dict(tokenizer_obj=tokenizer_obj,
                                        seq_text_data=seq_text_data,
                                        pos_condition=pos_condition)
    seq_word_score_object = run_feature_selection(tokenized_documents=cached_dict)

    # ------------------------------------------------------------------------
    # フレーズで特徴量抽出の場合
    ngram_cached_dict = construct_ngram_cached_dict(tokenizer_obj=tokenizer_obj,
                                                    seq_text_data=seq_text_data,
                                                    pos_condition=pos_condition,
                                                    n_value=2)
    seq_ngram_score_object = run_feature_selection(tokenized_documents=ngram_cached_dict)
    # ------------------------------------------------------------------------
    # 別のタスクの利用するので、単語の特徴量抽出は結果を保存しておきます
    with open('./models/word_score_soa.json', 'w') as f:
        f.write(json.dumps(seq_word_score_object, ensure_ascii=False))

if __name__ == '__main__':
    ### MecabWrapperを作る ###
    mecab_obj = MecabWrapper(dictType='ipadic', path_mecab_config='/usr/local/bin/')
    ### 取得したい品詞だけを定義する ###
    pos_condition = [('名詞', '固有名詞'), ('動詞', '自立'), ('形容詞', '自立')]

    ### wikipedia fullデータを読み込み ###
    print('=' * 50)
    path_wikipedia_full_json = './wikipedia_data/wikipedia-full.json'
    with open(path_wikipedia_full_json, 'r') as f:
        seq_wiki_full_text = json.load(f)

    main(tokenizer_obj=mecab_obj,
         pos_condition=pos_condition,
         seq_text_data=seq_wiki_full_text)
