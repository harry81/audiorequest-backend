from fabric.api import local, prefix


def pycodestyle():
    with prefix(". $VIRTUAL_ENV/bin/activate"):
        local("pycodestyle --config=setup.cfg")
    local("flake8 --config=setup.cfg")
    local("vulture stt --exclude=\"*/migrations/*\" --min-confidence 90")


def deploy(force=False, env='staging', test=True, notice=True):
    pycodestyle()
    local('zappa update dev_stt')
