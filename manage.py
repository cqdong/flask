#-*- coding:utf-8 -*-

import os
from app import create_app, db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Shell, Manager
# from app.models import User, Role, Post

app = create_app(os.environ.get('FLASK_CONFIG'))

manager = Manager(app)
migrate = Migrate(app)

def make_shell_context():
    return dict(app=app, db=db)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()