from JapaneseTokenizer import MecabWrapper
from typing import List, Tuple, Dict, Union, Any
from DocumentFeatureSelection.models import PersistentDict
import json
import tempfile
import os
import logging
import itertools
logger = logging.getLogger()
logger.setLevel(10)

SLEEP_TIME = 2

"""特徴量抽出で作ったスコアモデルを使って、カテゴリ分類を実施します。
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


def save_into_cached_dictionary(dict_object:Dict[str, List[List[str]]], cached_dict_object:PersistentDict)->PersistentDict:
    for key, values in dict_object.items():
        if not key in cached_dict_object:
            cached_dict_object[key] = values
        else:
            cached_dict_object[key] += values

    del dict_object
    return cached_dict_object


def reformat_dictionary(score_dictionary,
                        batch_size=10000,
                        is_use_cache=False):
    # type: (List[Dict[str,Any]], int)->Union[PersistentDict, Dict[str, List[Tuple[str,float]]]]
    """* What you can do
    - 辞書の形を変形します。
    * Input
    >>> [{"label": "レストラン", "score": 0.02942301705479622, "word": "お金"}]
    * Output
    >>> {"お金": [("レストラン", 0.02942301705479622)]}
    """
    temporary_dir = tempfile.mkdtemp()
    if is_use_cache:
        word_score_dictionary = PersistentDict(os.path.join(temporary_dir, 'temporary_dict.json'))
    else:
        word_score_dictionary = {}

    logger.info(msg="Loaded N(record)={}".format(len(score_dictionary)))

    if is_use_cache:
        counter = 0  # type: int
        temporary_dict_obj = {}

        for score_object in score_dictionary:
            score_tuple = (score_object['label'], score_object['score'])
            if not score_object['word'] in temporary_dict_obj:
                temporary_dict_obj[score_object['word']] = [score_tuple]
            else:
                temporary_dict_obj[score_object['word']].append(score_tuple)

            counter += 1
            if counter % batch_size == 0:
                word_score_dictionary = save_into_cached_dictionary(temporary_dict_obj, word_score_dictionary)
                del temporary_dict_obj
                temporary_dict_obj = {}
                logger.info(msg='Processed {} records now.'.format(counter))
    else:
        for score_object in score_dictionary:
            score_tuple = (score_object['label'], score_object['score'])
            if not score_object['word'] in word_score_dictionary:
                word_score_dictionary[score_object['word']] = [score_tuple]
            else:
                word_score_dictionary[score_object['word']].append(score_tuple)

    return word_score_dictionary



def get_text_score(input_text:str,
                   word_score_dictionary:Dict[str, List[Tuple[str,float]]],
                   tokenizer_obj:MecabWrapper,
                   pos_condition:List[Tuple[str,...]]):
    """* What you can do
    - スコアリング関数
    - カテゴリごとにスコアを算出することができます。
    """
    key_function = lambda tuple_obj: tuple_obj[0]
    list_tokens = tokenize_text(input_text=input_text, tokenizer_obj=tokenizer_obj, pos_condition=pos_condition)
    seq_score_elements = [word_score_dictionary[token] for token in list_tokens if token in word_score_dictionary]

    score_category = []
    for key_name, grouped_obj in itertools.groupby(sorted(itertools.chain.from_iterable(seq_score_elements), key=key_function, reverse=True), key=key_function):
        category_score = sum([score_tuple[1] for score_tuple in grouped_obj])
        score_category.append((key_name, category_score))

    return sorted(score_category, key=lambda tuple_obj: tuple_obj[1], reverse=True)


def evaluate_result(gold_label,
                    predicred_result):
    # type: (str, List[Tuple[str, float]])->Tuple[str, bool]
    """* What you can do
    - 評価用の文書の正解ラベルと予測結果の比較をします。
    """
    seq_category_name = set([category_name_tuple[0] for category_name_tuple in predicred_result])
    if gold_label in seq_category_name: return (gold_label, True)
    else: return (gold_label, False)


def  get_result_statistics(seq_result_tuple:List[Tuple[str, bool]])->None:
    """* What you can do
    - カテゴリごとに性能評価を出す
    """
    key_function = lambda eval_res_tuple: eval_res_tuple[0]

    seq_eval_result = [(tuple_eval_result[0], tuple_eval_result[1]) for tuple_eval_result in seq_result_tuple]
    g_object = itertools.groupby(sorted(seq_eval_result, key=key_function, reverse=True), key=key_function)
    for category_name, seq_eval_res in g_object:
        seq_result_flags = [seq_eval_tuple[1] for seq_eval_tuple in seq_eval_res]
        accuracy_of_category = len([res_flag for res_flag in seq_result_flags if res_flag is True]) / len(seq_result_flags)
        logger.info(msg='Accuracy of category={}; {} = {} / {}'.format(category_name,
                                                                        accuracy_of_category,
                                                                        len([res_flag for res_flag in seq_result_flags if res_flag is True]),
                                                                        len(seq_result_flags)))


def main(word_score_model:List[Dict[str,Any]],
         seq_evaluation_data:List[Dict[str,Any]],
         tokenizer_obj:MecabWrapper,
         pos_condition:List[Tuple[str,...]],
         ranking_evaluation:int=3):
    ### モデル辞書ファイルを変形; ついでにcache dictにしておく ###
    dict_word_model = reformat_dictionary(score_dictionary=word_score_model)

    flags = []
    ### wikipediaリードテキストに対する評価 ###
    for evaluation_obj in seq_evaluation_data:
        #### スコアリングの実施 ####
        seq_score_tuple = get_text_score(input_text=evaluation_obj['text'],
                                         word_score_dictionary=dict_word_model,
                                         tokenizer_obj=tokenizer_obj,
                                         pos_condition=pos_condition)
        #### 評価 ####
        tuple_boolean_flag = evaluate_result(gold_label=evaluation_obj['gold_label'],
                                       predicred_result=seq_score_tuple[:ranking_evaluation])
        logger.info(msg='Page-name={} -> Evaluation-flag={}, Score = {}'.format(evaluation_obj['page_title'],
                                                                        tuple_boolean_flag[1],
                                                                        seq_score_tuple[:ranking_evaluation]))
        flags.append(tuple_boolean_flag)

    ### 評価の統計値算出 ###
    true_flags = [True for tuple_flag in flags if tuple_flag[1] is True]
    logger.info(msg='='*40)
    logger.info(msg='Accuracy of wikipedia summary text when rank={}'.format(ranking_evaluation))
    logger.info(msg='Accuracy; {} = {} / {}'.format(len(true_flags)/len(flags), len(true_flags), len(flags)))
    ### カテゴリごとの正解率統計算出に対する評価 ###
    get_result_statistics(flags)
    logger.info('+'*40)



if __name__ == '__main__':
    ### MecabWrapperを作る ###
    mecab_obj = MecabWrapper(dictType='ipadic', path_mecab_config='/usr/local/bin/')
    ### 取得したい品詞だけを定義する ###
    pos_condition = [('名詞', '固有名詞'), ('動詞', '自立'), ('形容詞', '自立')]

    ### スコアモデルデータを読み込み ###
    path_word_model_json = './models/word_score_soa.json'
    with open(path_word_model_json, 'r') as f:
        word_score_model = json.load(f)

    ### 評価用文書の読み込み ###
    path_evaluation_document = './wikipedia_data/wikipedia-evaluation-full.json'
    with open(path_evaluation_document, 'r') as f:
        seq_evaluation_data = json.loads(f.read())

    main(word_score_model=word_score_model,
         seq_evaluation_data=seq_evaluation_data,
         tokenizer_obj=mecab_obj,
         pos_condition=pos_condition,
         ranking_evaluation=1)
    main(word_score_model=word_score_model,
         seq_evaluation_data=seq_evaluation_data,
         tokenizer_obj=mecab_obj,
         pos_condition=pos_condition,
         ranking_evaluation=3)
