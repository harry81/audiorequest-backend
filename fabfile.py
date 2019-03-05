import os
import random

from fabric.api import local, prefix, prompt

DEV_VIRTUAL_ENV = "-".join((os.getenv('VIRTUAL_ENV'), 'dev'))

conf_frontend = dict(staging=dict(distribution_id='E21XU2RF101HF8',
                                  subdomain='staging'),
                     prod=dict(distribution_id='E2QQLPBKZQB2D4',
                               subdomain='www'))


def pycodestyle():
    with prefix(". %s/bin/activate" % DEV_VIRTUAL_ENV):
        local("pycodestyle --config=setup.cfg")
    local("vulture stt --exclude=\"*/migrations/*\" --min-confidence 90")


def _sanity_check(force=False, env='staging'):

    branch = local("git rev-parse --abbrev-ref HEAD", capture=True)

    if env != 'prod':
        return True

    if branch != 'develop' and not force:
        print("Sanity : You are on [%s], not [master]." % branch)

    a = random.randint(1, 9)
    b = random.randint(1, 9)
    result = prompt('You\'re deploying on production. \n  %d + %d = ?' % (a, b))

    if not (int(result) == a + b):
        print("Sanity : Calm down on deploying")
        return False
    return True


def stt_backend_deploy(force=False, env='staging', test=True, notice=True):
    pycodestyle()
    local('zappa update {env}_stt'.format(**dict(env=env)))
    local('zappa manage {env}_stt migrate'.format(**dict(env=env)))


def stt_frontend_deploy(force=False, env='staging'):
    with prefix("cd ../frontend/;. %s/bin/activate" % DEV_VIRTUAL_ENV):
        local("ng build --configuration=%s" % env)
        local("aws s3 rm s3://{subdomain}.hoodpub.com --recursive".format(**conf_frontend[env]))
        local("aws s3 cp dist/stt-frontend s3://{subdomain}.hoodpub.com --recursive  --acl public-read".
              format(**conf_frontend[env]))
        local("aws configure set preview.cloudfront true")
        local("aws cloudfront create-invalidation --distribution-id {distribution_id} --paths '/*'".
              format(**conf_frontend[env]))


def stt_deploy(force=False, env='staging', component='both'):
    kwargs = dict(force=force, env=env)

    _sanity_check(force, env)

    if component in ['frontend', 'both']:
        stt_frontend_deploy(**kwargs)

    if component in ['backend', 'both']:
        stt_backend_deploy(**kwargs)
