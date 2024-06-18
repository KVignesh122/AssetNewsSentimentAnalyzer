from setuptools import setup, find_packages

setup(
    name='asset_sentiment_analyzer',
    version='0.1.4',
    description='A sentiment analyzer package for financial assets and securities utilizing GPT models.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/KVignesh122/AssetNewsSentimentAnalyzer',
    author='Kumaravel Vignesh',
    author_email='k_vignesh@hotmail.com',
    license='Apache-2.0',
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
    python_requires='>=3.6',
)
