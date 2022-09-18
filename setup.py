from setuptools import setup


dependencies = [
    'aiohttp',
    'aio_pika',
    'aioredis',
    'pika',
]


setup(
    name='awe',
    description='aiohttp websocket examples',
    author='Hmn Falahi',
    author_email='hmnfalahi@gmail.com',
    install_requires=dependencies,
)

