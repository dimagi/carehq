import os
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


def _setup_pact_production():
    env.virtualenv_root = '/home/carehq/.virtualenvs/carehq' #todo: change pact user to carehq
    env.src_root       = _join(env.root, 'src')
    env.code_root       = _join(env.root, 'src/carehq')
    env.project_root    = _join(env.root, 'src/carehq')


def pact_production():
    """ use pact_production environment on remote host for PACT"""
    env.code_branch = 'develop'
    env.sudo_user = 'carehq'
    env.hosts = ['10.84.168.247']
    env.environment = 'pact_production'
    env.user = prompt("Username: ", default=env.user)
    _setup_pact_production()

def _setup_mepi_production():
    env.virtualenv_root = '/home/mepimoz/.virtualenvs/carehq'
    env.src_root       = _join(env.root, 'src')
    env.code_root       = _join(env.root, 'src/carehq')
    env.project_root    = _join(env.root, 'src/carehq')

def mepi_production():
    """ use mepi_production environment on remote host for MEPI"""
    env.code_branch = 'shine'
    env.sudo_user = 'carehq'
    env.hosts = ['10.84.168.99']
    env.environment = 'mepi_production'
    env.user = prompt("Username: ", default=env.user)
    _setup_mepi_production()

def _setup_shine_staging():
    env.virtualenv_root = '/home/dimagivm/.virtualenvs/carehq_shine'
    env.root = '/home/dimagivm/'
    env.src_root       = _join(env.root, 'src')
    env.code_root       = _join(env.root, 'src/carehq')
    env.project_root    = _join(env.root, 'src/carehq')

def shine_staging():
    """Staging environment within local network
    """
    env.code_branch = 'shine'
    env.sudo_user = 'dimagivm'
    env.hosts = ['192.168.7.224']
    env.environment = 'shine_staging'
    env.user = prompt("Username: ", default='dimagivm')
    _setup_shine_staging()

def enter_virtualenv():
    """
    modify path to use virtualenv's python

    usage:

        with enter_virtualenv():
            run('python script.py')
    """
    return prefix('PATH=%(virtualenv_root)s/bin/:PATH' % env)

def get_code():
    """Get code for the first time
    """
    require('root', provided_by=('staging', 'pact_production', 'mepi_production'))
    with cd(env.src_root):
        if not files.exists(os.path.join(env.src_root, 'carehq')):
            sudo('git clone %(code_repo)s' % env, user=env.sudo_user)
        else:
            update()
        sudo('ln -s %(code_root)s/services/production/upstart/carehq_celery.conf /etc/init/' % env, shell=False)
        sudo('ln -s %(code_root)s/services/production/upstart/carehq_django.conf /etc/init/' % env, shell=False)
        sudo('ln -s %(code_root)s/services/production/upstart/carehq_formsplayer.conf /etc/init/' % env, shell=False)

def pip_update():
    """
    Do a pip update off the requirements file
    """
    with cd(env.code_root):
        with enter_virtualenv():
            run('pip install -r requirements.txt')

def syncdb():
    with cd(env.code_root):
        with enter_virtualenv():
            sudo('python manage.py syncdb --noinput', user=env.sudo_user)
            #sudo('python manage.py migrate --noinput', user=env.sudo_user)
            sudo('python manage.py collectstatic --noinput', user=env.sudo_user)

def update():
    """
    Update codebase and submodules (git pull)
    """
    require('root', provided_by=('staging', 'pact_production', 'mepi_production'))
    with cd(env.code_root):
        sudo('git checkout %(code_branch)s' % env, user=env.sudo_user)
        sudo('git pull', user=env.sudo_user)
        sudo('git submodule init', user=env.sudo_user)
        sudo('git submodule update', user=env.sudo_user)

def deploy_all():
    """ deploy code to remote host by checking out the latest via git """
    require('root', provided_by=('staging', 'pact_production','mepi_production'))
    if env.environment == 'pact_production':
        if not console.confirm('Are you sure you want to deploy pact_production?', default=False):
            utils.abort('Production deployment aborted.')
    
    if files.exists(env.code_root) == False:
        get_code()
    update_code()
    restart_all()

def restart_django():
    require('root', provided_by=('staging', 'pact_production', 'mepi_production'))
    with settings(sudo_user="root"):
        sudo('stop carehq_django', user=env.sudo_user, shell=False)
        sudo('initctl reload-configuration', user=env.sudo_user, shell=False)
        sudo('start carehq_django', user=env.sudo_user, shell=False)

def restart_celery():
    require('root', provided_by=('staging', 'pact_production', 'mepi_production'))
    with settings(sudo_user="root"):
        sudo('stop carehq_celery', user=env.sudo_user, shell=False)
        sudo('initctl reload-configuration', user=env.sudo_user, shell=False)
        sudo('start carehq_celery', user=env.sudo_user, shell=False)

        sudo('stop carehq_celerymon', user=env.sudo_user, shell=False)
        sudo('initctl reload-configuration', user=env.sudo_user, shell=False)
        sudo('start carehq_celerymon', user=env.sudo_user, shell=False)


def restart_formsplayer():
    require('root', provided_by=('staging', 'pact_production','mepi_production'))
    with settings(sudo_user="root"):
        sudo('stop carehq_formsplayer', user=env.sudo_user, shell=False)
        sudo('initctl reload-configuration', user=env.sudo_user, shell=False)
        sudo('start carehq_formsplayer', user=env.sudo_user, shell=False)


def restart_all():
    """ restart cchq_www service on remote host.  This will call a stop, reload the initctl to
    have any config file updates be reloaded into intictl, then start carehq again.
    """
    require('root', provided_by=('staging', 'pact_production', 'mepi_production'))
    restart_django()
    restart_celery()
    restart_formsplayer()

