import re


def auto_link(text):
    '''HTTP等のURLがあったらリンクにする'''
    return re.sub('(https?|ftp|news)(://[0-9a-zA-z\+\$\;\?\.%,!#~*/:@&=_-]+)',
    '<a href=\"\\1\\2\" target=\"_blank\">\\1\\2</a>',
    text)


def comment_fix(text):
    ## 引用符(>)があったら色を変える
    return re.sub('(^|>)(&gt;[^<]*)', '\\1<font color=red>\\2</font>', text)


def email_link(text):
    ## メールが入っていたらリンクにする
    name, email = text
    if email is not None and not email == '':
        ret = '<a href="mailto:{email}">{name}</a>'.format(email=email, name=name)
    else:
        ret = name
    return ret
