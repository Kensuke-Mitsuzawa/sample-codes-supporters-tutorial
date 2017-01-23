from typing import List, Tuple, Dict, Union
import wikipedia
import json
import time
import traceback
import logging
import tqdm
import os
logger = logging.getLogger()
logger.setLevel(10)

SLEEP_TIME = 2

"""サンプルとして利用するテキストデータを生成します。
wikipediaからテキストを選択し、ローカルディレクトリに保存します。
その際に、適当な文書ラベルを付与しています。
Python3.5.1の環境下で動作を確認しています。
"""

__author__ = "Kensuke Mitsuzawa"
__author_email__ = "kensuke.mit@gmail.com"
__license_name__ = "MIT"


def get_wikipedia_page(page_title):
    # type: (str) -> Union[bool, str]
    try:
        logger.debug('Got full page page-title={}'.format(page_title))
        return wikipedia.page(page_title).content
    except:
        logger.error(traceback.format_exc())
        return False


def get_wikipedia_summary(page_title:str, n_summary_sentence:int=3):
    # type: (str, int)->Union[bool, str]
    try:
        logger.debug('Got summary page page-title={}'.format(page_title))
        return wikipedia.summary(page_title, n_summary_sentence)
    except:
        logger.error(traceback.format_exc())
        return False


def main(path_extracted_wikipedia_text:str,
         wikipedia_article_names:List[Tuple[str, str]]):
    wikipedia.set_lang('ja')
    extracted_summary_text = []
    for article_name in tqdm.tqdm(wikipedia_article_names):
        text = get_wikipedia_summary(article_name[0])
        wikipedia_text_format = {}
        wikipedia_text_format["page_title"] = article_name[0]
        wikipedia_text_format["text"] = text
        wikipedia_text_format["gold_label"] = article_name[1]
        if not text is False:
            extracted_summary_text.append(wikipedia_text_format)
        time.sleep(SLEEP_TIME)

    with open(os.path.join(path_extracted_wikipedia_text, 'wikipedia-summary.json'), 'w') as f:
        f.write(json.dumps(extracted_summary_text, ensure_ascii=False, indent=4))

    extracted_full_text = []
    for article_name in tqdm.tqdm(wikipedia_article_names):
        text = get_wikipedia_page(article_name[0])
        wikipedia_text_format = {}
        wikipedia_text_format["page_title"] = article_name[0]
        wikipedia_text_format["text"] = text
        wikipedia_text_format["gold_label"] = article_name[1]
        if not text is False:
            extracted_full_text.append(wikipedia_text_format)
        time.sleep(SLEEP_TIME)

    with open(os.path.join(path_extracted_wikipedia_text, 'wikipedia-full.json'), 'w') as f:
        f.write(json.dumps(extracted_full_text, ensure_ascii=False, indent=4))



if __name__ == '__main__':
    path_extracted_wikipedia_dir = './wikipedia_data'
    training_data_wikipedia_article_names = [
        ### 映画 ###
        ("スター・ウォーズ エピソード4/新たなる希望", "映画"),
        ("大脱走", "映画"),
        ("史上最大の作戦", "映画"),
        ("遠すぎた橋", "映画"),
        ("特攻大作戦", "映画"),
        ("雨に唄えば", "映画"),
        ("ティファニーで朝食を", "映画"),
        ("ANNIE / アニー", "映画"),
        ("ウエスト・サイド物語(映画)", "映画"),
        ("ブルース・ブラザース", "映画"),
        ("フットルース(1984年の映画)", "映画"),
        ("グラン・トリノ", "映画"),
        ("インディ・ジョーンズ / 魔宮の伝説", "映画"),
        ### テレビ番組名 ###
        ("世界の果てまでイッテQ!", "テレビ番組"),
        ("日経スペシャル 未来世紀ジパング〜沸騰現場の経済学〜", "テレビ番組"),
        ("日経スペシャル カンブリア宮殿", "テレビ番組"),
        ("開運!なんでも鑑定団", "テレビ番組"),
        ("真田丸 (NHK大河ドラマ)", "テレビ番組"),
        ("坂の上の雲 (テレビドラマ)", "テレビ番組"),
        ("秘密のケンミンSHOW", "テレビ番組"),
        ("和風総本家", "テレビ番組"),
        ("ぴったんこカン・カン", "テレビ番組"),
        ### アルコール類 ###
        ("第三のビール", "アルコール"),
        ("ウイスキー", "アルコール"),
        ("ブランデー", "アルコール"),
        ("バーボン・ウイスキー", "アルコール"),
        ("日本酒", "アルコール"),
        ("焼酎", "アルコール"),
        ("竹鶴 (ウイスキー)", "アルコール"),
        ("ブラックニッカ", "アルコール"),
        ("ワイルドターキー", "アルコール"),
        ("オールド・パー", "アルコール"),
        ("旭酒造 (山口県)", "アルコール"),
        ### 外食・店舗 ###
        ("大戸屋ホールディングス", "レストラン"),
        ("マクドナルド", "レストラン"),
        ("昭和お好み焼き劇場うまいもん横丁", "レストラン"),
        ("立ち食いそば・うどん店", "レストラン"),
        ("ジョナサン (ファミリーレストラン)", "レストラン"),
        ("バーミヤン (レストランチェーン)", "外食・店舗-レストラン"),
        ("あきんどスシロー", "レストラン"),
        ### バイク ###
        ("ヤマハ・SR", "バイク"),
        ("ホンダ・アフリカツイン", "バイク"),
        ("ホンダ・VTR", "バイク"),
        ("ホンダ・VTR1000F", "バイク"),
        ("ホンダ・VFR", "バイク"),
        ("ヤマハ・TZR", "バイク"),
        ("ヤマハ・XT1200Zスーパーテネレ", "バイク"),
        ("ホンダ・CB400スーパーフォア", "バイク"),
        ("カワサキ・Dトラッカー", "バイク"),
        ("スズキ・バンディット400", "バイク"),
        ("スズキ・GSX1300Rハヤブサ", "バイク"),
        ### スマートフォン ###
        ("iPhone 6", "スマートフォン"),
        ("Xperia", "スマートフォン"),
        ("Nokia E71", "スマートフォン"),
        ("SoftBank 705NK", "スマートフォン"),
        ("Google Nexus", "スマートフォン"),
        ("Samsung Galaxy", "スマートフォン"),
        ("AQUOS PHONE", "スマートフォン"),
        ("ASUS ZenFone", "スマートフォン"),
        ### PC ###
        ("VAIO", "パソコン"),
        ("Let'snote", "パソコン"),
        ("MacBook", "パソコン"),
        ("iMac", "パソコン"),
        ("LAVIE", "パソコン"),
        ("ThinkPad", "パソコン"),
        ("ダイナブック (東芝)", "パソコン"),
        ("Inter Link", "パソコン"),
        ("Eee PC", "パソコン"),
        ### レジャー施設 ###
        ("ユニバーサル・スタジオ・ジャパン", "レジャー施設"),
        ("志摩スペイン村", "レジャー施設"),
        ("リトルワールド", "レジャー施設"),
        ("スペースワールド", "レジャー施設"),
        ("ムツゴロウ動物王国", "レジャー施設"),
        ### 鉄道関係 ###
        ("山手線", "鉄道"),
        ("新宿駅", "鉄道"),
        ("中央本線", "鉄道"),
        ("芸備線", "鉄道"),
        ("東海道本線", "鉄道"),
        ("奥羽本線", "鉄道"),
        ("軌間可変電車", "鉄道"),
        ("インターシティ", "鉄道"),
        ("ユーロスター", "鉄道"),
        ("TGV", "鉄道"),
        ### 教育関係 ###
        ("奈良先端科学技術大学院大学", "教育"),
        ("Z会", "教育"),
        ("東進ハイスクール", "教育"),
        ("大学院大学", "教育"),
        ("日本ジャーナリスト専門学校", "教育"),
        ("HAL (専門学校)", "教育"),
        ("日本大学東北高等学校", "教育"),
        ("PL学園中学校・高等学校", "教育"),
        ("学習院初等科", "教育"),
    ]
    main(path_extracted_wikipedia_dir, training_data_wikipedia_article_names)

