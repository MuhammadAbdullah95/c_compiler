import sys

_args = []
x = 5
y = 10
def add(a, b):
    _args = []
    t1 = a + b
    return t1

def main():
    _args = []
    label = 'start'
    while True:
        if label == 'start':
            _args.append(x)
            _args.append(y)
            t2 = add(*_args); _args = []
            z = t2
            t3 = z > 10
            if not t3: label = 'L1'; continue
            print(z)
            label = 'L2'; continue
        elif label == 'L1':
            pass
            label = 'L2'
        elif label == 'L2':
            pass
            break

if __name__ == '__main__':
    if 'main' in globals():
        main()