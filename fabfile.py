from fabric.api import local

def run_tests():
    local('manage.py test actors', capture=True)

