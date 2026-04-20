try:
    from Desc.BsaeDesc import BaseDescription
except ImportError:
    from .BsaeDesc import BaseDescription

__all__ = ["BaseDescription"]
