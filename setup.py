from setuptools import setup, find_packages

setup(
    name='asset_sentiment_analyzer',
    version='0.1.0',
    description='A sentiment analyzer package for financial assets and securities utilizing GPT models.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/KVignesh122/AssetNewsSentimentAnalyzer',
    author='Kumaravel Vignesh',
    author_email='k_vignesh@hotmail.com',
    license='MIT',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
)
