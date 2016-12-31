import pytest
from opentrons.tracker import tracker


@pytest.fixture
def robot():
    from opentrons import robot, instruments, containers
    robot.reset()

    trough = containers.load('trough', 'A1', 'trough')
    plate = containers.load('96-flat', 'A2', 'plate')
    p200 = instruments.Pipette(axis='a', name='p200')

    return robot, trough, plate, p200


def test_aspirate(robot):
    robot, trough, plate, p200 = robot

    tracker.init(robot, {
        'trough': {
            'A1': {
                'red': 100
            },
            'A2': {
                'green': 100
            },
            'A3': {
                'blue': 100
            }
        }
    })

    p200.aspirate(100, trough['A1']).dispense(100, plate['A1'])
    p200.aspirate(100, trough['A2']).dispense(100, plate['A1'])
    p200.aspirate(100, plate['A1']).dispense(100, plate['A2'])

    robot.simulate()

    res = tracker.state()

    assert res['plate']['A1'] == {
        'red': 50,
        'green': 50
    }

    assert res['plate']['A2'] == {
        'red': 50,
        'green': 50
    }
