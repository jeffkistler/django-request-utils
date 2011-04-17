import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'django-request-utils',
    version = '0.1a',
    license = 'BSD',
    description = '',
    long_description = read('README'),
    author = 'Jeff Kistler',
    author_email = 'jeff@jeffkistler.com',
    url = 'https://github.com/jeffkistler/django-request-utils',
    packages = ['request_utils', 'request_utils.templatetags'],
    package_dir = {'': 'src'},
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
