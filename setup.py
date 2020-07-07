from setuptools import setup

setup(
    name='python-uiflows',
    version='0.1.0',
    py_modules=['uiflows'],
    url='',
    license='MIT',
    author='hironei',
    author_email='',
    description='designing UI flows',
    python_requires='>=3.5',
    install_requires=[
        "setuptools>=46.4.0",
        "pydot>=1.4.1",
        "pyyaml>=5.3.1",
    ],
    entry_points={
        'console_scripts': [
            'uiflows= uiflows:uiflows',
        ],
    },
)
