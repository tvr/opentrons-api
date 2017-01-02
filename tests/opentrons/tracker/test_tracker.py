import pytest
from opentrons.tracker import tracker


@pytest.fixture
def liquids():
    state = {
        'trough': {
            'A1': {
                'red': 1000
            },
            'A2': {
                'green': 1000
            },
            'A3': {
                'blue': 1000
            }
        },
        'plate': {
            'A1': {
                'red': 100,
                'green': 100,
                'blue': 100
            }
        }
    }

    return state


def test_total_volume():
    state = {
        'red': 100,
        'green': 30,
        'blue': 20
    }
    assert tracker.total_volume(state) == 150


def test_substract():
    state = {
        'red': 90,
        'green': 60,
        'blue': 30
    }

    new_state, volume = tracker.substract(state, 30)
    assert new_state == {
        'red': 75,
        'green': 50,
        'blue': 25
    }
    assert volume == {
        'red': 15,
        'green': 10,
        'blue': 5
    }


def test_add():
    state_1 = {
        'red': 100,
        'green': 100
    }

    state_2 = {
        'red': 10,
        'green': 10,
        'blue': 100
    }

    res = tracker.add(state_1, state_2)
    assert res == {
        'red': 110,
        'green': 110,
        'blue': 100
    }


def test_aspirate():
    state = tracker.aspirate(liquids(), 100, 'p200', ('trough', 'A1'))

    assert state['p200'] == {
        'red': 100
    }
    assert state['trough'] == {
        'A1': {
            'red': 900
        },
        'A2': {
            'green': 1000
        },
        'A3': {
            'blue': 1000
        }
    }


def test_aspirate_dispense():
    state = tracker.aspirate(liquids(), 100, 'p200', ('trough', 'A1'))
    state = tracker.dispense(state, 50, 'p200', ('plate', 'A1'))

    assert state['p200'] == {
        'red': 50
    }
    assert state['plate'] == {
        'A1': {
            'red': 150,
            'green': 100,
            'blue': 100
        }
    }


def test_aspirate_multi():
    state = tracker.aspirate(liquids(), 90, 'p200', ('plate', 'A1'))

    assert state['p200'] == {
        'red': 30,
        'green': 30,
        'blue': 30
    }
    assert state['plate'] == {
        'A1': {
            'red': 70,
            'green': 70,
            'blue': 70
        }
    }


def test_aspirate_unknown():
    state = {
        'p200': {
            'red': 100
        },
        'plate': {
            'A1': {
                'red': 100
            }
        }
    }
    res = tracker.aspirate(state, 100, 'p200', ('plate', 'B1'))

    assert res['p200'] == {
        'red': 100,
        'unknown-from-plate-B1': 100
    }


def test_concentrations():
    res = tracker.concentrations(liquids())
    expected = {
        'trough': {
            'A1': {
                'red': 1.0
            },
            'A2': {
                'green': 1.0
            },
            'A3': {
                'blue': 1.0
            }
        },
        'plate': {
            'A1': {
                'red': 0.3333333333333333,
                'green': 0.3333333333333333,
                'blue': 0.3333333333333333
            }
        }
    }
    assert res == expected


def test_ensure_keys():
    a = {}
    res = tracker.ensure_keys(a, ['a', 'b'])

    assert res == {
        'a': {
            'b': {}
        }
    }


def test_event_traceable():
    from opentrons import instruments, containers
    plate = containers.load('96-flat', 'A1')
    pipette = instruments.Pipette(axis='b', max_volume=200)
    pipette.aspirate(100, plate[0])
    pipette.dispense(plate[1])
