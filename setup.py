from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='tinkertanker-pdfgen',
    version='0.0.1',
    author='Eric Yulianto',
    author_email='eric@tinkertanker.com',
    description='Tinkertanker Simple PDF Generator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='git@bitbucket.org:tinkertanker/tinkertanker-pdfgen.git',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.5',
    install_requires=[
        'PyPDF2==1.26.0',
        'reportlab==3.5.34',
        'Pillow==7.0.0'
    ],
    entry_points={
        'console_scripts': [
            'tinkertanker_pdfgen = pdfgen.__main__:main'
        ],
    },
)
