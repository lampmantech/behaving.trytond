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
                 admin_password='',
                 super_pwd=None,
                 config_file=None):
        OrigConfigModule.Config.__init__(self)
        # FixMe: straighten this mess out

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
                if not super_pwd:
                    sys.stderr.write(
                        "WARN: No super_pwd to create db %s\n" % (database_name,))
                    #! This is NOT the postgres server password
                    #! This calls security.check_super(password)
                    #! which is set in the conf file, [session]super_pwd
                    #! using crypt to generate it from from the command line
                    #! We default it to admin which may also be the
                    #! of the user 'admin': admin_password
                    super_pwd = 'admin'

                assert admin_password, "ERROR: No admin_password to create db " + database_name
                sys.stderr.write(
                    "create %s %s %s %s\n" % (database_name, super_pwd, language, admin_password,))
                create(database_name, super_pwd, language, admin_password)

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
                user='admin', language='en_US', password='admin',
                config_file=None):
    'Set trytond package as backend'
    admin_password = password
    super_pwd = 'admin'
    sTrytonConfigFile = config_file
    assert database_name
    os.environ['DB_NAME'] = database_name
    assert sTrytonConfigFile and os.path.isfile(sTrytonConfigFile)
    os.environ['TRYTOND_CONFIG'] = sTrytonConfigFile
    # this is required - should this info be in the tryton config file?
    assert 'PGPASSWORD' in os.environ and os.environ['PGPASSWORD'], \
		"Set PGPASSWORD in the OS environment to be the postgres password"
    postgres_password = os.environ['PGPASSWORD'] # 'postgresTryton'
    assert 'PGUSER' in os.environ and os.environ['PGUSER'], \
		"Set PGUSER in the OS environment to be the postgres user"
    postgres_user  = os.environ['PGUSER']        # 'tryton'
    if 'PGHOST' in os.environ and os.environ['PGHOST']:
        postgres_host = os.environ['PGHOST']
    else:
        postgres_host = '127.0.0.1'
    if 'PGPORT' in os.environ and os.environ['PGPORT']:
        postgres_port = os.environ['PGPORT']
    else:
        postgres_port = '5432'
    # this is partly in the uri field in the tryton config file?
    #? what's os.environ['TRYTOND_DATABASE_URI']
    database_uri = 'postgresql://%s:%s@%s:%s/%s' % (
        postgres_user, postgres_password, postgres_host, postgres_port, database_name,
    )
    del postgres_password, postgres_user

    # morons - trytond-3.4.4-py2.7.egg/trytond/backend/postgresql/database.py
    OrigConfigModule._CONFIG.current = TrytondConfig(database_uri, user,
                                                     admin_password=admin_password,
                                                     super_pwd=super_pwd,
                                                     language=language,
                                                     config_file=sTrytonConfigFile)
    return OrigConfigModule._CONFIG.current
