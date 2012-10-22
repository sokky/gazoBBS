import mimetypes
import gridfs.errors
from gazobbs import conf


class model:
    '''
    model class
    '''

    def __init__(self, db):
        self.db = db
        self.fs = gridfs.GridFS(db)

    def sel_one(self, table, *args, **kwargs):
        return self.db[table].find_one(*args, **kwargs)

    def sel_one_clm(self, table, where={}, clm={}):
        return self.db[table].find_one(where, clm)

    def sel_all(self, table, **where):
        return self.db[table].find(where)

    def sel_all_clm(self, table, where={}, clm={}):
        return self.db[table].find(where, clm)

    def ins(self, table, **data):
        return self.db[table].save(data, safe=True)

    def update(self, table, data, where):
        '''data,whereともにDict型のみ'''
        return self.db[table].update(where, {'$set': data}, safe=True)

    def update_push(self, table, data, where):
        '''data,whereともにDict型のみ'''
        return self.db[table].update(where, {'$push': data}, safe=True)

    def update_pull(self, table, data, where):
        '''data,whereともにDict型のみ'''
        return self.db[table].update(where, {'$pull': data}, safe=True)

    def save_file(self, data, filename):
        content, n = mimetypes.guess_type(filename)
        self.fs.put(data, filename=filename, content_type=content)

    def get_file(self, filename):
        try:
            return self.fs.get_last_version(filename)
        except gridfs.errors.NoFile:
            return None

    def delete_file(self, pict, thumb):
        file = self.get_file(pict)
        self.fs.delete(file._id)
        if conf.USE_THUMB:
            files = self.get_file(thumb)
            self.fs.delete(files._id)

    def seq(self):
        # SEQを取得し、なかったら初期化
        seqdata = self.db[conf.SEQ].find_and_modify(query={'name': 'seqno'},
                                                    update={"$inc": {"seq": 1}},
                                                    new=True)
        if seqdata == None:
            self.db[conf.SEQ].save({'name': 'seqno', 'seq': 1})
            ret = 1
        else:
            ret = seqdata['seq']
        return ret

    def del_data(self, table, **where):
        return self.db[table].remove(where, safe=True)

    def del_tree(self, _id, pict, thumb, only_pict):
        if not only_pict:
            self.del_data(conf.TBL_LOG, _id=_id)
        self.delete_file(pict, thumb)

    def del_res(self, no, pict, thumb, only_pict):
        if not only_pict:
            self.update_pull(conf.TBL_LOG, {'res': {'no': no}}, {'res.no': no})
        self.delete_file(pict, thumb)


class User(object):
    def __init__(self, password, groups=None):
        self.password = password
        self.groups = groups or []

    def check_password(self, passwd):
        return self.password == passwd
