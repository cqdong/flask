#-*- coding:utf-8 -*-

import os
from app import create_app, db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Shell, Manager
# from app.models import User, Role, Post
import config

path_env = os.path.join(config.basedir, '.env')
if os.path.exists(path_env):
    print('Importing environment from.env...')
    for line in open(path_env):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

    if os.environ.get('FLASK_CONFIG') == 'production':
        config.ProductionConfig.SQLALCHEMY_DATABASE_URI = os.environ.get('PRO_DATABASE_URL')
        config.Config.SECRET_KEY = os.environ.get('SECRET_KEY')

app = create_app(os.environ.get('FLASK_CONFIG'))

manager = Manager(app)
migrate = Migrate(app)

def make_shell_context():
    return dict(app=app, db=db)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()