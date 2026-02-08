import sys
import os

print("CWD:", os.getcwd())
print("sys.path:", sys.path)

try:
    import umucyo_mvp
    print("Imported umucyo_mvp:", umucyo_mvp)
    import umucyo_mvp.wsgi
    print("Imported umucyo_mvp.wsgi:", umucyo_mvp.wsgi)
except ImportError as e:
    print("ImportError:", e)
