from setuptools import setup, find_packages

setup(name="corpusanalysis",
      version="0.1.0,
      description="Description",
      author="ALain Herreman ",
      author_email="alain.herreman@univ-rennes1.fr",
      url="https://github.com/papillonperdu/corpusanalysis",
      install_requires=['numpy', 'matplotlib'],
      classifiers=CLASSIFIERS,
      packages=find_packages(exclude=['notebooks',
                                      'doc',
                                      'examples',
                                      'test_*']))
