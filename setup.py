from setuptools import setup

setup(name='pynmodl',
      version='0.1',
      description='NMODL parsing and compiling tools',
      url='http://github.com/borismarin/pynmodl',
      author='Boris Marin',
      author_email='borismarin@gmail.com',
      license='MIT',
      packages=['pynmodl'],
      package_data={'pynmodl': ['tests/sample_mods/*.mod', 'grammar/*.tx',
                                'tests/parsing/*.dat']},
      zip_safe=False,
      setup_requires=['pytest-runner'],
      install_requires=['textx', 'xmltodict'],
      tests_require=['pytest', 'textx', 'xmltodict'],
      )