from distutils.core import setup
from txTraderClient.version import VERSION, DESCRIPTION
setup(
  name='txTraderClient',
  version=VERSION,
  description=DESCRIPTION,
  author='Reliance Systems, Inc.',
  author_email='mkrueger@rstms.net',
  url='https://github.com/rstms/txtrader-client/',
  packages=['txTraderClient'],
  scripts=['scripts/txtrader']
)
