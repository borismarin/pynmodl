from setuptools import setup

setup(name='tx_nmodl',
      version='0.1',
      description='NMODL parsing and compiling tools',
      url='http://github.com/borismarin/nmodl-lems',
      author='Boris Marin',
      author_email='borimsarin@gmail.com',
      license='GPL3',
      packages=['tx_nmodl'],
      package_data={'tx_nmodl': ['tests/sample_mods/*.mod']},
      zip_safe=False,
      setup_requires=['pytest-runner'],
      install_requires=['textX'],
      tests_require=['pytest', 'textX', 'xmltodict'],
      )