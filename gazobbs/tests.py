import datetime
import unittest
import gazobbs.views as views
import gazobbs.myfilters as fil
from pyramid import testing
from gazobbs import conf
from unittest.mock import patch


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.time = datetime.datetime(2012, 10, 1, 20, 0)

        class fakedatetime(datetime.datetime):
            @classmethod
            def now(cls):
                return self.time
        patcher = patch('datetime.datetime', fakedatetime)
        self.addCleanup(patcher.stop)
        patcher.start()

    def tearDown(self):
        testing.tearDown()

    def test_auto_link(self):
        st = 'no html'
        res = 'no html'
        self.assertEqual(fil.auto_link(st), res)

        st = 'http://www.yahoo.co.jp'
        res = '<a href="http://www.yahoo.co.jp" target="_blank">http://www.yahoo.co.jp</a>'
        self.assertEqual(fil.auto_link(st), res)

        st = 'かいわhttp://www.yahoo.co.jp'
        res = 'かいわ<a href="http://www.yahoo.co.jp" target="_blank">http://www.yahoo.co.jp</a>'
        self.assertEqual(fil.auto_link(st), res)

        st = 'http://www.yahoo.co.jpてすと'
        res = '<a href="http://www.yahoo.co.jp" target="_blank">http://www.yahoo.co.jp</a>てすと'
        self.assertEqual(fil.auto_link(st), res)

        st = 'http://ja.wikipedia.org/wiki/%E6%95%B0%E7%8B%AC'
        res = '<a href="http://ja.wikipedia.org/wiki/%E6%95%B0%E7%8B%AC" target="_blank">http://ja.wikipedia.org/wiki/%E6%95%B0%E7%8B%AC</a>'
        self.assertEqual(fil.auto_link(st), res)

    def test_comment_fix(self):
        st = 'no html'
        res = 'no html'
        self.assertEqual(fil.comment_fix(st), res)

        st = '&gt;引用される'
        res = '<font color=red>&gt;引用される</font>'
        self.assertEqual(fil.comment_fix(st), res)

        st = '&lt;tag&gt; test &lt;/tag&gt;'
        res = '&lt;tag&gt; test &lt;/tag&gt;'
        self.assertEqual(fil.comment_fix(st), res)

        st = 'とちゅうでは&gt;引用されない'
        res = 'とちゅうでは&gt;引用されない'
        self.assertEqual(fil.comment_fix(st), res)

    def test_email_link(self):
        st = ('name', 'mail@jp.com')
        res = '<a href="mailto:mail@jp.com">name</a>'
        self.assertEqual(fil.email_link(st), res)

        st = ('name', '')
        res = 'name'
        self.assertEqual(fil.email_link(st), res)

        st = ('name', None)
        res = 'name'
        self.assertEqual(fil.email_link(st), res)

    def test_get_trip1(self):
        self.assertEqual(views.get_trip('123'), '</b>◆トリップなし<b>')

    def test_clean_str(self):
        st = ' <tag> test </tag> '
        res = '&lt;tag&gt; test &lt;/tag&gt;'
        self.assertEqual(views.clean_str(st, None), res)

        admin = 'admin'
        res = '<tag> test </tag>'
        self.assertEqual(views.clean_str(st, admin), res)

    def test_get_id(self):
        st = 'test'
        res = '76fc1fc7'
        self.assertEqual(views.get_id(st), res)

    def test_digest_passwd(self):
        st = 'test'
        res = '8f6bcd'
        self.assertEqual(views.digest_passwd(st), res)

    def test_get_date_str0(self):
        email = "a"
        host = "b"
        res = '2012/10/01(月)20:00:00 ID:0c55bea8'
        self.assertEqual(views.get_date_str(email, host), res)

    def test_get_date_str1(self):
        conf.DISP_ID = 1
        email = "a"
        host = 'b'
        res = '2012/10/01(月)20:00:00 ID:???'
        self.assertEqual(views.get_date_str(email, host), res)

    def test_get_date_str2(self):
        #日付取得系はmockを使うこと
        conf.DISP_ID = 1
        email = ""
        host = 'b'
        res = '2012/10/01(月)20:00:00 ID:0c55bea8'
        self.assertEqual(views.get_date_str(email, host), res)

    '''
    def test_usr_del_chk(self):
        from gazobbs.model import model
        from pymongo import Connection
        con = Connection('localhost', 27017)
        db = con['gazodb']
        md = model(db)
        print(md.sel_one('log', no='94', pwd=views.digest_passwd('1234')))
        print(views.usr_del_chk(['94'], '1234', md))
    '''
