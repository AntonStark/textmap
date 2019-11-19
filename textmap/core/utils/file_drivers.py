import typing as t

from core.utils.index_stuff import register_file_driver


def paragraph_seq(path):
    with open(path, 'r') as tf:
        for paragraph in tf.readlines():
            yield [paragraph]


class AbstractFileDriver:
    def paragraph_sequence(self, file: t.TextIO) -> t.Iterable[str]:
        pass


@register_file_driver('txt')
class PlainTextDriver(AbstractFileDriver):
    def paragraph_sequence(self, file: t.TextIO) -> t.Iterable[str]:
        yield from file.readlines()
