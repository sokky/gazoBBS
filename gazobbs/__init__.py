from pyramid.config import Configurator
from pyramid.events import subscriber, NewRequest
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pymongo import Connection

#DB用定義
DB_NAME = 'gazodb'
CONN_SV = 'localhost'
CONN_PORT = 27017


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    #session
    my_session_factory = UnencryptedCookieSessionFactoryConfig('secret')

    config = Configurator(settings=settings,
                          session_factory=my_session_factory)

    #MongoDB Connect
    conn = Connection(CONN_SV, CONN_PORT)
    config.registry.settings['db_conn'] = conn

    def add_mongo_db(event):
        #接続情報格納
        settings = event.request.registry.settings
        db = settings['db_conn'][DB_NAME]
        event.request.db = db

    config.add_subscriber(add_mongo_db, NewRequest)
    config.add_route('gazo_bbs', '/img_board')
    config.add_route('gazo_bbs_page', '/img_board/{page}')
    config.add_route('gazo_bbs_res', '/img_board/res/{res}')
    config.add_route('img', '/img/{file_name}')
    config.add_route('regist', '/regist')
    config.add_route('user_del', '/userdel')

    #static
    config.add_static_view(name='', path='static', cache_max_age=3600)

    #template
    config.add_settings({'mako.directories': 'gazobbs:templates'})

    #認証(authentication)と権限(authorization)
    authentication_policy = AuthTktAuthenticationPolicy('seekrit')
    authorization_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authentication_policy)
    config.set_authorization_policy(authorization_policy)

    config.scan('gazobbs')
    return config.make_wsgi_app()

if __name__ == '__main__':
    #Localでの実行環境用
    from wsgiref.simple_server import make_server
    #Server Start
    app = main({})
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
