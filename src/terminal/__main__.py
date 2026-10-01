import asyncio

from .app import main

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nbye (the interrupted question is not stored)")
