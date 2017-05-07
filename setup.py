from setuptools import setup

setup(name='tx_nmodl',
      version='0.1',
      description='NMODL parsing and compiling tools',
      url='http://github.com/borismarin/nmodl-lems',
      author='Boris Marin',
      author_email='borismarin@gmail.com',
      license='MIT',
      packages=['tx_nmodl'],
      package_data={'tx_nmodl': ['tests/sample_mods/*.mod', 'grammar/*.tx']},
      zip_safe=False,
      setup_requires=['pytest-runner'],
      install_requires=['textx', 'xmltodict'],
      tests_require=['pytest', 'textx', 'xmltodict'],
      )