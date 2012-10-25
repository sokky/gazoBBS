import os
import re
import time
import math
import pymongo
import hashlib
import datetime
import logging
import tempfile
import urllib.parse
from PIL import Image
from gazobbs import conf
from gazobbs.model import model
from gazobbs.dto import log
from pyramid.view import view_config, notfound_view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.response import Response


def usr_del(del_no, passwd, md, chk):
    '''ユーザ削除のパスワードチェック'''
    ret = []
    tree_list = []
    res_list = []
    for no in del_no:
        # treeからnoで検索
        tmp1 = md.sel_one(conf.TBL_LOG, {'no': no,
                                         'pwd': digest_passwd(passwd)})
        if tmp1:
            tree_list.append(tmp1)
        else:
            # treeに無い場合はresから検索
            tmp2 = md.sel_one(conf.TBL_LOG, {'res.no': no,
                                             'res.pwd': digest_passwd(passwd)})
            if tmp2:
                for d in tmp2['res']:
                    res_list.append(d) if d['no'] == no else None
            else:
                ret.append('No.{no}の削除パスワードが間違っています。'.format(no=no))
    if ret:
        # パスワードがひとつでも間違っていた場合はエラー文言を返却
        return ret
    for res in res_list:
        # 先にres削除（同じtreeの場合エラーになるため）
        md.del_res(res['no'], res['pict'], res['thumb'], chk)
    for tree in tree_list:
        # tree削除
        md.del_tree(tree['_id'], tree['pict'], tree['thumb'], chk)
    return []


def del_over_tree(md):
    '''ログ行数オーバーで削除
    '''
    start = int(conf.LOG_MAX)
    tmp = md.sel_all_clm(conf.TBL_LOG, clm={'_id': 1,
                                            'pict': 1,
                                            'thumb': 1}).sort('no',
                                                              pymongo.ASCENDING).skip(start)
    for data in tmp:
        md.del_tree(data['_id'], data['pict'], data['thumb'])


def chk_double_post(md, host):
    '''二重投稿チェック
    '''
    # 同じホストで投稿時間が連続投稿秒数内のデータがある場合はエラー(スレッド)
    tim = datetime.datetime.now()
    tim = tim - datetime.timedelta(seconds=conf.RENZOKU)
    data = md.sel_all_clm(conf.TBL_LOG, {'host': host,
                                         'last_update_date': {'$gte': tim}})
    if data.count() > 0:
        return True

    # 同じホストで投稿時間が連続投稿秒数内のデータがある場合はエラー(レス)
    data = md.sel_all_clm(conf.TBL_LOG, {'res.host': host,
                                         'res.last_update_date': {'$gte': tim}})
    if data.count() > 0:
        return True

    return False


def chk_delete_soon(md, treelst):
    '''もうすぐ消えるチェック
    '''
    start = int(conf.LOG_MAX * 0.95)
    tmp = md.sel_all_clm(conf.TBL_LOG, clm={'no': 1}).sort('no',
                                                          pymongo.DESCENDING).skip(start)
    nolist = [t['no'] for t in tmp]
    # スレッド主のnoが最大ログ保持数の95％より後ろの場合はもうすぐ削除フラグを立てる。
    for tree in treelst:
        if tree['no'] in nolist:
            tree['del_soon'] = '1'
        else:
            tree['del_soon'] = '0'
    return treelst


def get_trip(key):
    """トリップを計算する。
    """
    trip = ''
    try:
        from crypt import crypt
        key.replace('&amp', '&')
        key.replace('&#44', ',')
        salt = key.join('H.')[1:3]
        salt = re.sub('[^\.-z]', '.', salt)
        salt = salt.translate(str.maketrans(':;<=>?@[\\]^_`', 'ABCDEFGabcdef'))
        trip = crypt(key, salt)
        trip = trip[-10:]
    except ImportError:
        trip = 'トリップなし'
    return '</b>◆' + trip + '<b>'


def clean_str(st, admin):
    '''前後の空欄を削除してタグを無効化
    '''
    import cgi

    st = st.strip()
    if not admin:   # adminモードのときだけタグOK
        st = cgi.escape(st, True)
        st = st.replace('&amp', '&')
    return st


def get_id(ip):
    '''ID生成
    '''
    d = datetime.datetime.now()
    m = hashlib.md5()
    m.update((ip + conf.IDSEED + d.strftime('%y%m%d')).encode())
    return m.hexdigest()[-8:]


def get_date_str(email, host):
    '''日付を日本語にする'''
    youbi = ['月', '火', '水', '木', '金', '土', '日']
    dt = datetime.datetime.now()
    nowdate = '%d/%0.2d/%0.2d' % (dt.year, dt.month, dt.day)
    nowdate += '(%s)' % youbi[dt.weekday()]
    nowdate += '%0.2d:%0.2d:%0.2d' % (dt.hour, dt.minute, dt.second)
    if conf.DISP_ID:
        if not email == '' and conf.DISP_ID == 1:
            nowdate += ' ID:???'
        else:
            nowdate += ' ID:' + get_id(host)
    return nowdate


def digest_passwd(string):
    '''暗号化
    '''
    m = hashlib.md5()
    m.update(string.encode())
    return m.hexdigest()[2:8]


def proxy_connect(ip, port):
    '''アクセスできたらプロクシとして認識する
    /だめならプロクシじゃないと判断する
    '''
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect((ip, port))
    except (socket.error, socket.timeout):
        return False
    return True


def imgsrc_fix(db, pict, thumb, W, H):
    '''IMGタグ作成
    :pict=画像ファイル名,thumb=サムネイルファイル名,W=幅,H=高さ
    '''
    imgsrc = ''
    if pict:
        md = model(db)
        file = md.get_file(pict)
        if file:
            size = file.length
            if W and H:
                if thumb:
                    imgsrc = '''
                    <small>サムネイルを表示しています.クリックすると元のサイズを表示します.</small><br>
                    <a href="/img/{src}" target="_blank">
                    <img src="/img/{thumb}" border=0 align="left" width={w} height={h} hspace=20 alt="{size} B">
                    </a>
                    '''.format(src=pict, thumb=thumb, size=size, w=W, h=H)
                else:
                    imgsrc = '''
                    <a href="/img/{src}" target="_blank">
                    <img src="/img/{src}" border=0 align="left" width={w} height={h} hspace=20 alt="{size} B">
                    </a>
                    '''.format(src=pict, size=size, w=W, h=H)
            else:
                imgsrc = '''
                <a href="/img/{src}" target="_blank">
                <img src="/img/{src}" border=0 align="left" hspace=20 alt="{size} B">
                </a>
                '''.format(src=pict, size=size)
            imgsrc = '''
            <a href="/img/{src}" target="_blank">{src}</a>-({size} B) {imgsrc}
            '''.format(src=pict, size=size, imgsrc=imgsrc)

    return imgsrc


def tree_fix(log, db):
    #pictの修正
    log['pict'] = imgsrc_fix(db, log['pict'], log['thumb'],
                                 log['W'], log['H'])
    return log


def get_log_count(db):
    '''log件数取得'''
    md = model(db)
    tmp = md.sel_all(conf.TBL_LOG)
    return tmp.count()


def getlog(db, res, page):
    '''記事取得
    '''
    md = model(db)
    start = page * conf.PAGE_DEF

    if not res == 0:
        tmp = md.sel_all(conf.TBL_LOG, no=res)
        if tmp.count() == 0:
            raise VariableError('該当記事が見つかりません')
    else:
        tmp = md.sel_all(conf.TBL_LOG).sort('last_update_date',
                                        pymongo.DESCENDING).skip(start).limit(conf.PAGE_DEF)
    treelst = [t for t in tmp]

    for tree in (treelst):
        #スレッド主の記事の修正
        tree = tree_fix(tree, db)
        reses = tree['res']
        for resone in reses:
            #レス記事の修正
            resone = tree_fix(resone, db)

    # もうすぐ消えるチェック
    treelst = chk_delete_soon(md, treelst)
    # デフォルト表示するチェック
    return treelst


def insertlog(request, param):
    '''記事保存
    '''
    md = model(request.db)

    com = param['com']
    sub = param['sub']
    name = param['name']
    email = param['email']
    resto = param['resto'] if param['resto'] else ''
    if (com in conf.badstring or sub in conf.badstring or
        name in conf.badstring or email in conf.badstring):
        return "拒絶されました"

    name = '' if re.search('^[ |　|]*$', name) else name
    com = '' if re.search('^[ |　|\t]*$', com) else com
    sub = '' if re.search('^[ |　|]*$', sub) else sub

    if not param['resto'] and not param['textonly'] and param['upfile'] == b'':
        return '画像がありません'
    if com == '' and param['upfile'] == b'':
        return '何か書いてください'

    # 名前欄の変更
    name = re.sub('管理', '"管理"', name)
    name = re.sub('削除', '"削除"', name)

    # 入力値長さチェック
    if len(com) > 1000:
        return '本文が長すぎますっ！'
    if len(name) > 100:
        return '本文が長すぎますっ！'
    if len(email) > 100:
        return '本文が長すぎますっ！'

    # HOST取得
    host = request.client_addr
    if host in conf.badip:
        return "拒絶されました"

    if (re.search('^mail', host) or re.search('^ns', host) or
        re.search('^dns', host) or re.search('^ftp', host) or
        re.search('^prox', host) or re.search('^pc', host)):
        pxck = True
    if (re.search('ne\\.jp$', host) or re.search('ad\\.jp$', host) or
        re.search('bbtec\\.net$', host) or re.search('aol\\.com$', host) or
        re.search('uu\\.net$', host) or re.search('asahi-net\\.or\\.jp$', host) or
        re.search('rim\\.or\\.jp$', host)):
        pxck = False
    else:
        pxck = True

    if pxck and conf.PROXY_CHECK:
        if proxy_connect(host, 80):
            return 'ＥＲＲＯＲ！　公開ＰＲＯＸＹ規制中！！(80)'
        if proxy_connect(host, 8080):
            return 'ＥＲＲＯＲ！　公開ＰＲＯＸＹ規制中！！(8080)'

    # No. とパスと時間とURLフォーマット
    import random
    pwd = param['pwd']
    random.seed()
    if pwd == '':
        if not 'pwdc' in request.cookies or not request.cookies['pwdc'] == '':
            pwd = ('00000000' + str(random.randrange(0, 99999999)))[-8:]
        else:
            pwd = request.cookies['pwdc']
    dig_pass = digest_passwd(pwd) if not pwd == '' else '*'

    #日付とID取得
    nowdate = get_date_str(email, host)

    # テキスト整形
    admin = 'admin' in request.session
    email = clean_str(email, admin)
    email = re.sub('[\r\n]', '', email)
    sub = clean_str(sub, admin)
    sub = re.sub('[\r\n]', '', sub)
    resto = clean_str(resto, admin)
    resto = re.sub('[\r\n]', '', resto)
    com = clean_str(com, admin)

    # 改行文字の統一
    com = com.replace('\r\n', '\n')
    com = com.replace('\r', '\n')

    # 連続する空行を一行
    com = re.sub('\n((　| )*\n){3,}', '\n', com)
    if not conf.BR_CHECK or com.count('\n') < conf.BR_CHECK:
        com = com.replace('\n', '<br>\n')
    com = com.replace('\n', '')

    name = re.sub('[\r\n]', '', name)
    name = re.sub('◆', '◇', name)
    names = name
    name = clean_str(name, admin)

    # トリップ作成
    m = re.search('(#|＃)(.*)', names)
    if m:
        cap = m.group(2)
        trip = get_trip(cap)
        name = re.sub('(#|＃)(.*)', '', name)
        name += trip

    if name == '':
        name = '名無し'
    if com == '':
        com = '本文なし'
    if sub == '':
        sub = '無題'

    # 二重投稿チェック
    if chk_double_post(md, host):
        return '連続投稿はもうしばらく時間を置いてからお願い致します'

    # ログ行数オーバー
    del_over_tree(md)

    # 更新
    savelog = log()

    # 画像保存
    if not param['upfile'] == b'':
        data = param['upfile'].file
        fname = param['upfile'].filename
        try:
            img = Image.open(data)
        except IOError:
            return "アップロードに失敗しました。画像ファイル以外は受け付けません"

        #拒否ファイル
        if hashlib.md5(img.tostring()).hexdigest() in conf.badfile:
            return "アップロードに失敗しました。同じ画像がありました"

        savelog.W, savelog.H = img.size
        pictname, savelog.ext = os.path.splitext(fname)
        tmpname = str(int(time.time()))
        savelog.pict = tmpname + savelog.ext
        if (savelog.W > conf.MAX_W or savelog.H > conf.MAX_H):
            tW = conf.MAX_W / savelog.W
            tH = conf.MAX_H / savelog.H
            if tW < tH:
                key = tW
            else:
                key = tH
            savelog.W = math.ceil(savelog.W * key)
            savelog.H = math.ceil(savelog.H * key)
            # サムネ作成
            if conf.USE_THUMB:
                f = tempfile.TemporaryFile()
                savelog.thumb = tmpname + '.s' + savelog.ext
                img.thumbnail((savelog.W, savelog.H), Image.ANTIALIAS)
                img.save(f, img.format)
                f.seek(0)   # SAVEするとポインタが最後まで飛ぶのでもどす
                md.save_file(f, savelog.thumb)
        data.seek(0)   # PILのOpenをするとポインタが最後まで飛ぶのでもどす
        md.save_file(data, savelog.pict)

        mes = "画像 {fname} のアップロードが成功しました".format(fname=fname)

    #スレ立て
    if resto == '':
        savelog.last_update_date = datetime.datetime.now()
        savelog.no = md.seq()
        savelog.now = nowdate
        savelog.name = name
        savelog.email = email
        savelog.sub = sub
        savelog.com = com
        savelog.host = host
        savelog.pwd = dig_pass
        savelog.res = []
        md.ins(conf.TBL_LOG, **savelog.__dict__)
    else:
        #レス
        savelog.last_update_date = datetime.datetime.now()
        savelog.no = md.seq()
        savelog.now = nowdate
        savelog.name = name
        savelog.email = email
        savelog.sub = sub
        savelog.com = com
        savelog.host = host
        savelog.pwd = dig_pass
        #レスを格納
        resData = {'res': savelog.__dict__}
        #レスを上書き
        whereData = {'no': int(resto)}
        if not md.update_push(conf.TBL_LOG, resData, whereData):
            return 'スレッドがありません。'
        #最終更新日時上書き
        dateData = {'last_update_date': datetime.datetime.now()}
        md.update(conf.TBL_LOG, dateData, whereData)


class VariableError(Exception):
    def __init__(self, msg):
        self.msg = msg


@notfound_view_config(append_slash=True)
def notfound(request):
    '''404発生（だったかな？）
    '''
    return HTTPNotFound('Not Found')


@view_config(context=VariableError, renderer='error.mak')
def err(exc, request):
    '''エラー発生時
    '''
    return {'errmsg': exc.msg}


@view_config(route_name='img')
def show_img(request):
    '''画像表示
    '''
    file_name = request.matchdict['file_name']
    md = model(request.db)
    file = md.get_file(file_name)

    response = Response()
    if file is not None:
        response.content_type = file.content_type
        response.app_iter = file
    else:
        response.content_type = 'image/jpeg'
        response.app_iter = open('nopict.jpg', 'rb')
    return response


@view_config(route_name='regist', request_method='GET')
def regist_log_error(request):
    '''GETははじく
    '''
    raise VariableError('不正な投稿をしないで下さい(GET)')


@view_config(route_name='user_del', request_method='POST')
def user_del(request):

    md = model(request.db)
    # 削除対象取得
    del_no = []
    for k, v in request.params.items():
        if v == 'delete':
            del_no.append(int(k))
    # passwd取得
    passwd = request.params['pwd']
    # 画像だけチェック取得
    try:
        chk = request.params['onlyimgdel']
        chk = True
    except KeyError:
        chk = False
    # passwdチェック 兼 削除
    ret = usr_del(del_no, passwd, md, chk)
    if len(ret):
        raise VariableError('<br>'.join(ret))
    # 削除完了文言
    request.session.flash('削除完了')
    # 次画面遷移先
    response = HTTPFound(location='/img_board')

    return response


@view_config(route_name='regist', request_method='POST')
def regist_log(request):
    '''掲示板投稿ボタン押下時
    [必要なパラメータ
    //name:おなまえ
    //email:E-mail
    //sub:題名
    //com:コメント
    //upfile:添付ファイル
    //pwd:削除キー
    //textonly:画像なしチェック
    //resto:レスするNo　なかったらスレ立て
    '''
    keylist = ['mode', 'name', 'email', 'sub', 'com',
               'upfile', 'pwd', 'textonly', 'resto']
    param = {}
    for key in keylist:
        try:
            param[key] = request.params[key]
        except KeyError:
            param[key] = None

    print(param)
    error = insertlog(request, param)
    if error:
        raise VariableError(error)

    # 投稿完了文言
    request.session.flash('投稿完了')
    # 次画面遷移先
    response = HTTPFound(location='/img_board')
    # Cookieセット
    expires = datetime.datetime.now() + datetime.timedelta(days=7)
    response.set_cookie('namec', value=urllib.parse.quote(param['name']), expires=expires)
    response.set_cookie('pwdc', value=param['pwd'], expires=expires)

    return response


@view_config(route_name='gazo_bbs', renderer='log.mak')
@view_config(route_name='gazo_bbs_page', renderer='log.mak')
@view_config(route_name='gazo_bbs_res', renderer='log.mak')
def show_bbs(request):
    '''掲示板TOP画面
    /必要なパラメータ
    /res:レスするNo　なかったら全件
    /page:現在ページ　なかったら先頭
    '''
    log = logging.getLogger(__name__)
    log.debug('test')

    #パラメータ受け取り
    try:
        res = int(request.matchdict['res'])
    except (KeyError, ValueError):
        res = 0

    try:
        page = int(request.matchdict['page'])
    except (KeyError, ValueError):
        page = 0

    # ログ取得
    logs = getlog(request.db, res, page)
    # ログ全件数取得
    count = get_log_count(request.db)
    return {'logs': logs, 'res': res, 'mode': '', 'admin': '',
            'page': page, 'count': count}


@view_config(route_name='login', renderer='admin_login.mak')
def show_login(request):

    return {'test': 'test'}
