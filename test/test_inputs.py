from pyqualw2.config.inputs import W2Con


def test_read_w2con_from_file(sample_w2_con):
    w2con = W2Con.from_file(sample_w2_con)

    assert w2con.us == [2, 34, 39, 44]
    assert w2con.ds == [31, 36, 41, 45]
    assert w2con.dltf == [0.9, 0.6, 0.9, 0.6, 0.9]
    assert w2con.nstr == [4, 0, 0, 0]
    assert w2con.dynstruc == [False, False, False, False]
