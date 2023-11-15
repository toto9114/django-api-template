from typing import Iterator


def generate_chunk(array: list[any], chunk_size: int) -> Iterator[list[any]]:
    if len(array) < 1:
        return

    for idx in range(0, len(array), chunk_size):
        yield array[idx : idx + chunk_size]
