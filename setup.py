from setuptools import setup

setup(
    name='aufmachen',
    version='0.2.1',
    url='http://github.com/fdb/aufmachen',
    license='BSD',
    author='Frederik & Jan De Bleser',
    author_email='frederik@burocrazy.com',
    description='Turns a website\'s HTML into nice, clean objects.',
    packages=['aufmachen', 'aufmachen.websites'],
    package_data = {'aufmachen': ['*.js']},
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

