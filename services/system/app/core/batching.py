

from typing import List


def create_batches(items: List, size: int) -> List:
    total_items = len(items)

    for index in range(0, total_items, size):
        yield items[index:min(index + size, total_items)]
