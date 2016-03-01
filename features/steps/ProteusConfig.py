# -*- encoding: utf-8 -*-

import os, sys
import urlparse

from proteus import config as OrigConfigModule

class TrytondConfig(OrigConfigModule.TrytondConfig):
    """
    Configuration for trytond.

    We restore the 3.2 behaviour of creating the database if it does not exist.

    
    """

    def __init__(self, database_uri=None, user='admin', language='en_US',
                 password='',
                 server_password=None,
                 config_file=None):
        OrigConfigModule.Config.__init__(self)
        # straighten this mess out
        
        if config_file is None:
            config_file = os.environ.get('TRYTOND_CONFIG')
        assert config_file and os.path.isfile(config_file), \
            "Set the environment variable TRYTOND_CONFIG to the path of TRYTOND CONFIG"
        
        if not database_uri:
            database_uri = os.environ.get('TRYTOND_DATABASE_URI')
        else:
            os.environ['TRYTOND_DATABASE_URI'] = database_uri
        assert os.path.isfile(config_file), \
            "set os.environ.get('TRYTOND_CONFIG') to be the Tryton config file"
            
        from trytond.config import config
        config.update_etc(config_file)
        
        from trytond.pool import Pool
        from trytond import backend
        from trytond.protocols.dispatcher import create
        from trytond.cache import Cache
        from trytond.transaction import Transaction
        self.database = database_uri
        database_name = None
        if database_uri:
            uri = urlparse.urlparse(database_uri)
            database_name = uri.path.strip('/')
        if not database_name:
            assert 'DB_NAME' in os.environ, \
                "Set os.environ['DB_NAME'] to be the database name"
            database_name = os.environ['DB_NAME']
        self.database_name = database_name
        self._user = user
        self.config_file = config_file

        Pool.start()
        if False:
           # new in 3.4
            self.pool = Pool(database_name)
            self.pool.init()
        else:
            # 3.2 code created the database if it did not exist            
            with Transaction().start(None, 0) as transaction:
                cursor = transaction.cursor
                databases = backend.get('Database').list(cursor)
            if database_name not in databases:
                # trytond/protocols/dispatcher.py
                '''
                Create a database

                :param database_name: the database name
                :param password: the server password
                :param lang: the default language for the database
                :param admin_password: the admin password
                :return: True if succeed
                '''
                if not server_password:
                    sys.stderr.write(
                        "WARN: No server_password to create db %s\n" % (database_name,))
                    server_password = 'postgresTryton' # os.environ['PGPASSWORD']
    
                    
                assert password, "ERROR: No password to create db " + database_name
                sys.stderr.write(
                    "create %s %s %s %s\n" % (database_name, server_password, language, password,))
                create(database_name, server_password, language, password)

            database_list = Pool.database_list()
            self.pool = Pool(database_name)
            if database_name not in database_list:
                self.pool.init()
            
        with Transaction().start(self.database_name, 0) as transaction:
            Cache.clean(database_name)
            User = self.pool.get('res.user')
            transaction.context = self.context
            self.user = User.search([
                ('login', '=', user),
                ], limit=1)[0].id
            with transaction.set_user(self.user):
                self._context = User.get_preferences(context_only=True)
            Cache.resets(database_name)


def set_trytond(database_name=None,
                user='admin', language='en_US', password='',
                config_file=None):
    'Set trytond package as backend'

    sTrytonConfigFile = config_file
    assert database_name
    os.environ['DB_NAME'] = database_name
    assert sTrytonConfigFile and os.path.isfile(sTrytonConfigFile)
    os.environ['TRYTOND_CONFIG'] = sTrytonConfigFile
    # this is required - even though the info is in the tryton config file - or is it?
    server_password = 'postgresTryton' # os.environ['PGPASSWORD']
    server_user  = 'tryton'            # os.environ['PGUSER']
    database_uri = 'postgresql://%s:%s@127.0.0.1:5432/%s' % (
        server_user, server_password, database_name,
    ) # os.environ['TRYTOND_DATABASE_URI']
        
    # morons - trytond-3.4.4-py2.7.egg/trytond/backend/postgresql/database.py
    OrigConfigModule._CONFIG.current = TrytondConfig(database_uri, user,
                                                     password=password,
                                                     language=language,
                                                     config_file=sTrytonConfigFile)
    return OrigConfigModule._CONFIG.current
