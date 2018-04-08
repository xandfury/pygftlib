from setuptools import setup
import pygftlib

setup(name='pygftlib',
      version=pygftlib.__version__,
      description='Simple gevent based file transfer library',
      scripts=['bin/pygftlib'],
      url='http://github.com/xandfury/pygftlib',
      author='Abhinav Saxena',
      author_email='xandfury@gmail.com',
      license='MIT',
      packages=['pygftlib'],
      classifiers=[
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 3 :: Only",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python",
      ],
      install_requires=open('requirements.txt').read().splitlines(),
      zip_safe=False)