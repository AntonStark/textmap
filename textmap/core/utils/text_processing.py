def paragraph_seq(path):
    with open(path, 'r') as tf:
        yield from tf.readlines()
