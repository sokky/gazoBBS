import json
from bson.objectid import ObjectId
from bson import json_util
from datetime import datetime


class mongoEncoder(json.JSONEncoder):
    def default(self, obj):
        #_idはObjectId型で、JSONではSerializeできない。よって変換する
        if isinstance(obj, ObjectId):
            return json_util.default(obj)
        elif isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return obj
        return json.JSONEncoder.default(self, obj)


class dto_base:
    def set(self, *tpr, **dic):
        m = mongoEncoder()
        for data in tpr:
            for key in data:
                setattr(self, key, m.default(data[key]))
        for key in dic:
            setattr(self, key, m.default(dic[key]))


class log(dto_base):
    def __init__(self):
        self.last_update_date = ''  # 最終更新時間
        self.no = ''        # レス番号
        self.now = ''       # 時間
        self.name = ''      # 投稿者
        self.email = ''     # メールアドレス
        self.sub = ''       # 題名
        self.com = ''       # コメント
        self.host = ''      # 書き込み者HOST
        self.pwd = ''       # 削除キー
        self.pict = ''      # 画像名（改名後）
        self.ext = ''       # 拡張子
        self.W = ''         # 表示用幅
        self.H = ''         # 表示用高さ
        self.thumb = ''     # サムネ画像名
        self.res = []       # レス（空配列にしておく）


class seq_tbl(dto_base):
    def __init__(self):
        self.name = ''
        self.seq = ''

if __name__ == '__main__':
    testlog = log()
    testlog.no = 1001
    testlog.now = '2012/08/31(金)20:11:25'
    testlog.name = 'ひろあき'
    testlog.email = 'test@example.com'
    testlog.sub = '無題'
    testlog.com = 'エロゲーの時間だおらぁ！'
    testlog.host = '127.0.0.1'
    testlog.pwd = '9999'
    testlog.ext = 'jpg'
    testlog.W = '200'
    testlog.H = '250'
    testlog.pict = '20120812160809594_0001.jpg'
    testlog.last_update_date = 'ISODate("2012-08-31T22:42:03.422Z")'

    reslog = log()
    reslog.no = 1002
    reslog.now = '2012/08/31(金)22:21:35'
    reslog.name = 'ひろあき'
    reslog.email = 'test1@example.com'
    reslog.sub = '無題'
    reslog.com = 'エロゲーの時間だおらぁ！'
    reslog.host = '127.0.0.1'
    reslog.pwd = '9999'
    reslog.ext = 'jpg'
    reslog.W = '200'
    reslog.H = '250'
    reslog.pict = '99999.jpg'

    testlog.res = reslog.__dict__
    print(testlog.__dict__)
