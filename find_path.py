import sys

def init_path(size):
    allow = []
    for i in range(size):
        for j in range(size):
            allow.append([i, j])
    return allow

def get_next_choice(step, hist, raws, allow):
    num = 0
    for raw in raws:
        nextstep = [raw[i]+step[i] for i in range(2)]
        if nextstep in allow and nextstep not in hist:
            num += 1
    return num

def search_next(size, pos, history, allow):
    nextsteps = {}
    raws = [[1,2], [1,-2], [2,1], [2,-1], [-1,2], [-1,-2], [-2,1], [-2,-1]]
    if len(history) == size*size:
        return True
    for raw in raws:
        nextstep = [raw[i]+pos[i] for i in range(2)]
        if nextstep in allow and nextstep not in history:
            next_choice = get_next_choice(nextstep, history, raws, allow)
            nextsteps[str(nextstep)] = next_choice
    nextsteps = sorted(nextsteps.items(), key=lambda d:d[1])

    for nextstep in nextsteps:
        nextstep = list(eval(nextstep[0]))
        history.append(nextstep)
        back = search_next(size, nextstep, history, allow)
        if back:
            return True
        else:
            history.pop()
    else:
        return False

def search_path(s, h):
    allow = init_path(s)
    position = h[-1]
    back = search_next(s, position, h, allow)
    if back:
        return h
    else:
        return False
