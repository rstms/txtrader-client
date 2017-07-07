from distutils.core import setup
from txtrader_client.version import VERSION, DESCRIPTION
setup(
  name='txtrader_client',
  version=VERSION,
  description=DESCRIPTION,
  author='Reliance Systems, Inc.',
  author_email='mkrueger@rstms.net',
  url='https://github.com/rstms/txtrader_client/',
  packages=['txtrader_client'],
  scripts=['scripts/txtrader']
)
