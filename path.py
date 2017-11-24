import sys

sys.setrecursionlimit(1000000)
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

def search_next(size, pos, history):
    allow = init_path(size)
    nextsteps = {}
    raws = [[1,2], [1,-2], [2,1], [2,-1], [-1,2], [-1,-2], [-2,1], [-2,-1]]
    if len(history) == size*size:
        return True
    for raw in raws:
        nextstep = [raw[i]+pos[i] for i in range(2)]
        if nextstep in allow and nextstep not in history:
            next_choice = get_next_choice(nextstep, history, raws, allow)
            nextsteps[next_choice] = nextstep
    sorted(nextsteps.items())
    
    for nextstep in nextsteps.values():
        history.append(nextstep)
        back = search_next(size, nextstep, history)
        if back:
            return True
        else:
            history.pop()
    else:
        return False

def search_path(size, position, history):
    history.append(position)
    back = search_next(size, position, history)
    if back:
        return history
    else:
        return False
