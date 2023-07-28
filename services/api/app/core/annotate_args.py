from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dataclasses import dataclass

    annotate_args = dataclass
else:

    def annotate_args(cls):
        return cls
