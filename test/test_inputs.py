from pyqualw2.config.inputs import W2Con


def test_read_w2con_from_file(sample_w2_con):
    w2con = W2Con.from_file(sample_w2_con)
