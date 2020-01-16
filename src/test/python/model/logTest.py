from model.log import resize, get_iterable_for_rb


def test_expand_from_zero():
    data = list(range(0, 10))
    newIdx = resize(10, 20, data, 0)
    expected = list(range(0, 10)) + ([None] * 10)
    assert data == expected
    assert newIdx == 0
    iterated = [i for i in get_iterable_for_rb(data, newIdx)]
    assert expected == iterated


def test_expand_middle():
    data = list(range(0, 10))
    newIdx = resize(10, 20, data, 5)
    expected = list(range(0, 10)) + ([None] * 10)
    assert data == expected
    assert newIdx == 5
    iterated = [i for i in get_iterable_for_rb(data, newIdx)]
    expectedIterated = list(range(5, 10)) + ([None] * 10) + list(range(0, 5))
    assert expectedIterated == iterated


def test_reduce_beginning():
    data = list(range(0, 10))
    newIdx = resize(10, 5, data, 0)
    expected = list(range(5, 10))
    assert data == expected
    assert newIdx == 0
    iterated = [i for i in get_iterable_for_rb(data, newIdx)]
    assert expected == iterated


def test_reduce_middle():
    data = list(range(0, 10))
    newIdx = resize(10, 5, data, 3)
    expected = [0, 1, 2, 8, 9]
    assert data == expected
    assert newIdx == 3
    iterated = [i for i in get_iterable_for_rb(data, newIdx)]
    assert [8, 9, 0, 1, 2] == iterated


def test_reduce_end():
    data = list(range(0, 10))
    newIdx = resize(10, 5, data, 8)
    expected = [3, 4, 5, 6, 7]
    assert data == expected
    assert newIdx == 4
    iterated = [i for i in get_iterable_for_rb(data, newIdx)]
    assert [7, 3, 4, 5, 6] == iterated
