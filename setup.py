from setuptools import setup, find_packages

setup(name="infpostgresql",
      version="0.0.1",
      author="Bifer Team",
      description="Postgres wrapper",
      platforms="Linux",
      packages=find_packages(exclude=["specs", "integration_specs"]),
      install_requires=[
          'psycopg==3.3.2',
          'psycopg-pool==3.3.0',
          'retrying==1.4.2',
          'infcommon'
      ],
      dependency_links=[
          'git+https://github.com/aleasoluciones/infcommon3.git#egg=infcommon'
      ]
)
