from textmap.settings import FILE_DRIVERS, LANGUAGE_PARSERS


def class_fullname(o):
    module = o.__module__
    if module is None or module == str.__class__.__module__:
        return o.__name__
    return module + '.' + o.__name__


def register_file_driver(file_type: str):
    def actual_register(cls):
        FILE_DRIVERS[file_type] = cls
        return cls
    return actual_register


def register_language_parser(language: str):
    def actual_register(cls):
        LANGUAGE_PARSERS[language] = cls
        return cls
    return actual_register
