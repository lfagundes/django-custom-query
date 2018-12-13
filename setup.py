from setuptools import setup, find_packages
import os

setup(name = 'django-custom-query',
      version = '0.3.0',
      description = 'Custom user query parser for Django ORM',
      long_description = open(os.path.join(os.path.dirname(__file__), "README")).read(),
      author = "Luis Fagundes",
      author_email = "lhfagundes@gmail.com",
      license = "The MIT License",
      packages = find_packages(),
      install_requires = ['django', 'sqlparse'],
      classifiers = [
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      url = 'http://django-custom-query.readthedocs.io/',
      
)
