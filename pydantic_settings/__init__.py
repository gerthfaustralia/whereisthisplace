import os

class BaseSettings:
    """Minimal stub of pydantic BaseSettings."""
    def __init__(self, **values):
        annotations = getattr(self, '__annotations__', {})
        for field in annotations:
            val = values.get(field, os.getenv(field))
            if val is not None:
                typ = annotations[field]
                try:
                    if typ is int:
                        val = int(val)
                    elif typ is float:
                        val = float(val)
                except Exception:
                    pass
            setattr(self, field, val)
