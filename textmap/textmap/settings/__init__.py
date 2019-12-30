from .common import *

if os.getenv('TEXTMAP_PRODUCTION_ENV', False):
    from .prod import *
else:
    from .dev import *
