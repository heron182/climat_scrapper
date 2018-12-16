from setuptools import setup

setup(
    name="climat_scrapper",
    version="1.0",
    description="A Climatempo scrapper",
    url="http://github.com/heron182/climat_scrapper",
    author="Heron Rossi",
    author_email="heron.rossi@hotmail.com",
    license="MIT",
    packages=["climat_scrapper"],
    install_requires=["beautifulsoup4==4.6.3", "pandas==0.23.4", "selenium==3.141.0", "lxml==4.2.5"],
    entry_points = {
        'console_scripts': ['climat_scrapper=climat_scrapper.scrapper:main'],
    },
    zip_safe=False,
)
