from functools import wraps
import inspect


def _quote(x):
    if isinstance(x, str):
        return '"%s"' % x
    else:
        return x


def trace(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        fa = inspect.getcallargs(fn, *args, **kwargs)
        arglist = ("%s=%s" % (k, _quote(v)) for k, v in fa.items() if k != "self")
        print("do.%s(%s)" % (fn.__name__, ", ".join(arglist)))

        return fn(*args, **kwargs)
    return wrapper
