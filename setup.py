from setuptools import setup, find_packages

setup(name="infpostgresql",
      version="0.0.1",
      author="Bifer Team",
      description="Simple postgres wrapper",
      platforms="Linux",
      packages=find_packages(
          exclude=["tests", "specs", "integration_specs", "functional_specs", "acceptance_specs"]),
      install_requires=[
          'psycopg2==2.8.6',
          'retrying==1.3.3',
      ],
      extras_require={
          'dev': [
              'packaging@https://github.com/aleasoluciones/pydevlib.git#egg=pydevlib',
          ]
      },
      dependency_links=[])
