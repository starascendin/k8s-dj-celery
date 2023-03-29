#!/usr/bin/env python
import os
import sys
from pathlib import Path
from django.conf import settings

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

    # start new section
    from django.conf import settings

    # if settings.DEBUG:
    #     if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
    #         print('#DEBUG settings.DEBUG', settings.DEBUG)
    #         import debugpy
    #         debugpy.listen(("0.0.0.0", 5678))
    #         print('Attached!')
    # end new section

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django  # noqa
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )

        raise

    # This allows easy placement of apps within the interior
    # aininjas directory.
    current_path = Path(__file__).parent.resolve()
    print("#current_path: ", current_path)
    sys.path.append(str(current_path / "aininjas"))
    # sys.path.append(str(current_path / "scripts"))

    execute_from_command_line(sys.argv)
