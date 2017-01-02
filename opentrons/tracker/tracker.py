from opentrons.util import trace


def event(data):
    pass


trace.EventBroker.get_instance().add(event)


def init(robot, state):
    # subscribe to aspirate/dispense traceables
    # set starting state
    pass


def ensure_keys(state, path):
    parent = state
    for p in path:
        if p not in parent:
            parent[p] = {}
        parent = parent[p]

    return state


def total_volume(state):
    return sum(state.values())


def concentrations(state):
    # if any of our children is a dict, go one level deeper
    # alternatively we can test if each is not a number
    if any((isinstance(value, dict) for value in state.values())):
        return {
            key: concentrations(value)
            for key, value in state.items()
        }

    t = total_volume(state)
    return {
        key: value / t
        for key, value in state.items()
    }


def substract(state, volume):
    d = volume / total_volume(state)
    new_state = {
        key: value * (1.0 - d)
        for key, value in state.items()
    }

    volume = {
        key: value - new_state[key]
        for key, value in state.items()
    }

    return new_state, volume


def add(state_1, state_2):
    res = {
        key: state_1.get(key, 0.0) + state_2.get(key, 0.0)
        for key in set(state_1) | set(state_2)
    }
    return res


def aspirate(state, volume, instrument, source):
    container, well = source
    state = ensure_keys(state, [instrument])

    # if aspirating from non-existent container/well
    # we'll make it known by marking a transfer volume
    volume_dict = {
        'unknown-from-{}-{}'.format(container, well): volume
    }

    if (container in state) and (well in state[container]):
        new_state, volume_dict = substract(state[container][well], volume)
        state[container][well] = new_state

    state[instrument] = add(volume_dict, state[instrument])
    return state


def dispense(state, volume, instrument, destination):
    container, well = destination
    state = ensure_keys(state, [container, well])

    new_state, volume = substract(state[instrument], volume)
    state[instrument] = new_state
    state[container][well] = add(volume, state[container][well])
    return state
