#画面用定義（画面制御に使うのでDictで保存）
TITLE = '画像掲示板'         # タイトル
SELF_NAME = 'img_board'     # 自分へのURL
USE_THUMB = 1               # 1:サムネイルをつくる 0:なし
RESIMG = 1                  # 1:レスに画像を張る 0:はらない
PAGE_DEF = 5                # 1ページに表示する記事数
ADMIN_PASS = 'admin_pass'   # 管理者パス
MAX_KB = 500                # MAX KB
MAX_W = 250                 # MAX 幅
MAX_H = 250                 # MAX 高さ
PROXY_CHECK = 0             # proxyの書込みを制限する y:1 n:0
DISP_ID = 2                 # ID表示  強制:2 する:1 しない:0
IDSEED = 'idの種'            # idの種
BR_CHECK = 15               # 改行を抑制する行数 しない:0
LOG_MAX = 300               # スレッドの最大数
RENZOKU = 5                 # 連続投稿秒数
RENZOKU2 = 10               # 画像連続投稿秒数

#DB用定義（画面制御には使わない）
TBL_LOG = 'log'             # 書き込みログTBL
SEQ = 'seq_tbl'             # SEQTBL
SEQ_LOG = 'log_no'          # SEQNO識別子

#その他定義
badstring = set()
badfile = set()
badip = set()
