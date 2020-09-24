from setuptools import setup, find_packages

setup(name='astrobase_services',
      version='1.9.0',
      description='AstroBase services',
      url='',
      author='Nico Vermaas',
      author_email='nvermaas@xs4all.nl',
      license='BSD',
      install_requires=['requests'],
      packages=find_packages(),
      #packages=['astrobase_services'],
      include_package_data=True,
      entry_points={
            'console_scripts': [
                  'astrobase_service=astrobase_services.astrobase_service:main',
            ],
      },
      scripts=['astrobase_scripts/astrobase_start_services.sh',
               'astrobase_scripts/astrobase_stop_services.sh'
               ],
      )