import fabric
from fabric.api import *
from fabric.contrib import console
from fabric import utils
from fabric.contrib import files

env.root = '/opt/carehq_project'
env.code_repo = 'git://github.com/dimagi/carehq.git'

def _join(*args):
    """
    We're deploying on Linux, so hard-code that path separator here.
    """
    return '/'.join(args)


def _setup_path():
    env.virtualenv_root = '/home/pact/.virtualenvs/carehq'
    env.src_root       = _join(env.root, 'src')
    env.code_root       = _join(env.root, 'src/carehq')
    env.project_root    = _join(env.root, 'src/carehq')

def production():
    """ use production environment on remote host"""
    env.code_branch = 'develop'
    env.sudo_user = 'pact'
    env.hosts = ['10.84.168.247']
    env.environment = 'production'
    env.user = prompt("Username: ", default=env.user)
    _setup_path()


def enter_virtualenv():
    """
    modify path to use virtualenv's python

    usage:

        with enter_virtualenv():
            run('python script.py')
    """
    return prefix('PATH=%(virtualenv_root)s/bin/:PATH' % env)

def get_code():
    require('root', provided_by=('staging', 'production'))
    with cd(env.src_root):
        sudo('git clone %(code_repo)s' % env, user=env.sudo_user)
        sudo('ln -s %(code_root)s/services/production/upstart/carehq_celery.conf /etc/init/')
        sudo('ln -s %(code_root)s/services/production/upstart/carehq_django.conf /etc/init/')
        sudo('ln -s %(code_root)s/services/production/upstart/carehq_formsplayer.conf /etc/init/')

def pip_update():
    with cd(env.code_root):
        with enter_virtualenv():
            run('pip install -r requirements.txt')

def update():
    require('root', provided_by=('staging', 'production'))
    with cd(env.code_root):
        sudo('git checkout %(code_branch)s' % env, user=env.sudo_user)
        sudo('git pull', user=env.sudo_user)
        sudo('git submodule init', user=env.sudo_user)
        sudo('git submodule update', user=env.sudo_user)
        with enter_virtualenv():
            sudo('python manage.py syncdb --noinput', user=env.sudo_user)
            #sudo('python manage.py migrate --noinput', user=env.sudo_user)
            sudo('python manage.py collectstatic --noinput', user=env.sudo_user)

def deploy_all():
    """ deploy code to remote host by checking out the latest via git """
    require('root', provided_by=('staging', 'production'))
    if env.environment == 'production':
        if not console.confirm('Are you sure you want to deploy production?', default=False):
            utils.abort('Production deployment aborted.')
    
    if files.exists(env.code_root) == False:
        get_code()
    update_code()
    restart_all()

def restart_django():
    require('root', provided_by=('staging', 'production'))
    with settings(sudo_user="root"):
        sudo('stop carehq_django', user=env.sudo_user, shell=False)
        sudo('initctl reload-configuration', user=env.sudo_user, shell=False)
        sudo('start carehq_django', user=env.sudo_user, shell=False)

def restart_celery():
    require('root', provided_by=('staging', 'production'))
    with settings(sudo_user="root"):
        sudo('stop carehq_celery', user=env.sudo_user, shell=False)
        sudo('initctl reload-configuration', user=env.sudo_user, shell=False)
        sudo('start carehq_celery', user=env.sudo_user, shell=False)

        sudo('stop carehq_celerymon', user=env.sudo_user, shell=False)
        sudo('initctl reload-configuration', user=env.sudo_user, shell=False)
        sudo('start carehq_celerymon', user=env.sudo_user, shell=False)


def restart_formsplayer():
    require('root', provided_by=('staging', 'production'))
    with settings(sudo_user="root"):
        sudo('stop carehq_formsplayer', user=env.sudo_user, shell=False)
        sudo('initctl reload-configuration', user=env.sudo_user, shell=False)
        sudo('start carehq_formsplayer', user=env.sudo_user, shell=False)


def restart_all():
    """ restart cchq_www service on remote host.  This will call a stop, reload the initctl to
    have any config file updates be reloaded into intictl, then start carehq again.
    """
    require('root', provided_by=('staging', 'production'))
    restart_django()
    restart_celery()
    restart_formsplayer()

