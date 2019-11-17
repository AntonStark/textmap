def paragraph_seq(path):
    with open(path, 'r') as tf:
        for paragraph in tf.readlines():
            yield [paragraph]
