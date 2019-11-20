import re
import typing as t

from core.utils.index_stuff import register_language_parser


class AbstractLanguageParser:
    def parse(self, paragraph_sequence: t.Iterable[str]) -> t.Iterable[t.List[str]]:
        pass

    def parse_sentence(self, sentence: str) -> t.Iterable[str]:
        pass


@register_language_parser('ru')
class SimpleRussianParser(AbstractLanguageParser):
    def __init__(self):
        self.SENTENCE_ENDS = ['...', '.', '?!', '?', '!']
        self.SENTENCE_STARTS = []   # todo возможное улучшение
        # вводим предикаты Имеет правильный конец? Имеет правильное начало?
        # на 1 вперёд заглядывающий проход последовательности
        #   в конце возвращаем последнюю часть без проверок
        # проверям не только предикат конца, но и предикат начала для следующей части

    def produce_end_rule(self):
        return '|'.join(map(lambda sep: r'\s*' + re.escape(sep) + r'\s*', self.SENTENCE_ENDS))

    def check_end(self, paragraph):
        source = paragraph.strip('\n ')
        return source[-1] in self.SENTENCE_ENDS if len(source) > 0 else True    # seq of only \n and ' ' may be end

    def parse(self, paragraph_sequence: t.Iterable[str]) -> t.Iterable[t.List[str]]:
        def process(buf):
            def chunks(l, n):
                """Yield successive n-sized chunks from l."""
                for i in range(0, len(l), n):
                    yield l[i:i + n]

            rule = self.produce_end_rule()
            sen_with_sep = re.split(f'({rule})', ' '.join(buf))
            sentences = filter(len, map(
                lambda sen_and_sep: ''.join(sen_and_sep),
                chunks(sen_with_sep, 2)
            ))
            yield list(sentences)

        bag = []
        for p in paragraph_sequence:
            bag.append(p)
            if self.check_end(p):
                yield from process(bag)
                bag.clear()
        if bag:
            yield from process(bag)

    def parse_sentence(self, sentence: str) -> t.Iterable[str]:
        return re.split('(\W+)', sentence)
