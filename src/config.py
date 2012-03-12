
import os

__all__ = ['RICO_PATH']

if "XDG_CONFIG_HOME" in os.environ:
    RICO_PATH = os.path.join(os.environ["XDG_CONFIG_HOME"], "ricodebug")
else:
    RICO_PATH = "%s/.ricodebug" % os.environ["HOME"]

if not os.path.exists(RICO_PATH):
    os.mkdir(RICO_PATH)

