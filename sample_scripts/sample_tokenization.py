from JapaneseTokenizer import MecabWrapper
from typing import List, Tuple, Dict, Union, Any
import json
import logging
import collections
import itertools
logger = logging.getLogger()
logger.setLevel(10)

SLEEP_TIME = 2

"""形態素分割のサンプルコードを示します
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


def aggregate_words(seq_tokenized:List[List[str]])->collections.Counter:
    """* What you can do
    - 形態素の集計カウントを実施する

    * Params
    - seq_tokenized
        >>> [['スター・ウォーズ', 'エピソード4', '新たなる希望', 'スター・ウォーズ', 'エピソード4', 'なる', 'きぼう', 'STAR WARS', 'IV', 'A NEW HOPE', '1977年', 'する', 'アメリカ映画']]

    """
    ### 二次元リストを１次元に崩す; List[List[str]] -> List[str] ###
    seq_words = itertools.chain.from_iterable(seq_tokenized)
    word_frequency_obj = collections.Counter(seq_words)
    return word_frequency_obj


def aggregate_words_by_label():
    """* What you can do
    -
    """
    pass


def main(tokenizer_obj:MecabWrapper,
         seq_text_data:List[Dict[str,Any]],
         pos_condition:List[Tuple[str,...]]):
    """* What you can do
    - 形態素解析機の呼び出し
    - 単語集計
    """
    # --------------------------------------------------------------------------------------------------------------#
    # 単純単語集計をする
    ### Python独特のリスト内包表記を利用する(リスト内包表記の方が実行速度が早い) ###
    seq_tokenized_text = [
        tokenize_text(input_text=wiki_text_obj['text'],tokenizer_obj=tokenizer_obj, pos_condition=pos_condition)
        for wiki_text_obj in seq_text_data
    ]
    ### 単語集計を実施する ###
    word_frequency_obj = aggregate_words(seq_tokenized_text)
    ### Counterオブジェクトはdict()関数で辞書化が可能 ###
    dict(word_frequency_obj)
    ### 頻度順にソートするために [(word, 頻度)] の形にする
    seq_word_frequency = [(word, frequency) for word, frequency in dict(word_frequency_obj).items()]
    ### 単語頻度順にソート ###
    print('Top 100 word frequency without label')
    print(sorted(seq_word_frequency, key=lambda x:x[1], reverse=True)[:100])

    # --------------------------------------------------------------------------------------------------------------#
    # ラベルごとに単語を集計する
    ### ラベル情報も保持しながら形態素分割の実行 ###
    seq_tokenized_text = [
        (wiki_text_obj['gold_label'], tokenize_text(input_text=wiki_text_obj['text'],tokenizer_obj=tokenizer_obj, pos_condition=pos_condition))
        for wiki_text_obj in seq_text_data
    ]
    #### ラベルごとの集約する ####
    ##### ラベルごとに集計するためのキーを返す匿名関数 #####
    key_function= lambda x:x[0]
    #### 必ず、groupbyの前にsortedを実施すること
    g_object = itertools.groupby(sorted(seq_tokenized_text, key=key_function), key=key_function)
    ### リスト内包表記化も可能。わかりやすさのために、通常のループ表記をする ###
    for label_name, element_in_label in g_object:
        ### element_in_label はgenerator objectで [(label, [word])]の構造を作る ###
        seq_list_tokens_with_label = list(element_in_label)
        seq_list_tokens = [label_tokens[1] for label_tokens in seq_list_tokens_with_label]
        word_frequency_obj_label = aggregate_words(seq_list_tokens)
        seq_word_frequency_label = [(word, frequency) for word, frequency in dict(word_frequency_obj_label).items()]
        print('*'*30)
        print('Top 100 words For label = {}'.format(label_name))
        print(sorted(seq_word_frequency_label, key=lambda x:x[1], reverse=True)[:100])


if __name__ == '__main__':
    ### MecabWrapperを作る ###
    mecab_obj = MecabWrapper(dictType='ipadic')
    ### 取得したい品詞だけを定義する ###
    pos_condition = [('名詞', '固有名詞'), ('動詞', '自立'), ('形容詞', '自立')]

    ### wikipedia summaryデータを読み込み ###
    print('=' * 50)
    path_wikipedia_summary_json = './wikipedia_data/wikipedia-summary.json'
    with open(path_wikipedia_summary_json, 'r') as f:
        seq_wiki_summary_text = json.load(f)


    main(tokenizer_obj=mecab_obj,
         pos_condition=pos_condition,
         seq_text_data=seq_wiki_summary_text)

    ### wikipedia fullデータを読み込み ###
    print('=' * 50)
    path_wikipedia_full_json = './wikipedia_data/wikipedia-full.json'
    with open(path_wikipedia_full_json, 'r') as f:
        seq_wiki_full_text = json.load(f)

    main(tokenizer_obj=mecab_obj,
         pos_condition=pos_condition,
         seq_text_data=seq_wiki_full_text)