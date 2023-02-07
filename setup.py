from setuptools import setup, find_packages

setup(name="infpostgresql",
      version="0.0.1",
      author="Bifer Team",
      description="Postgres wrapper",
      platforms="Linux",
      packages=find_packages(exclude=["specs", "integration_specs"]),
      install_requires=[
          'psycopg==3.0.8',
          'retrying==1.3.3',
          'infcommon'
      ],
      dependency_links=[
          'git+https://github.com/aleasoluciones/infcommon3.git#egg=infcommon'
      ]
)
