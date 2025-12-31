import sys

_args = []
def factorial(n):
    _args = []
    label = 'start'
    while True:
        if label == 'start':
            result = 1
            label = 'L1'
        elif label == 'L1':
            t1 = n > 1
            if not t1: label = 'L2'; continue
            t2 = result * n
            result = t2
            t3 = n - 1
            n = t3
            label = 'L1'; continue
        elif label == 'L2':
            return result

def main():
    _args = []
    num = 5
    _args.append(num)
    t4 = factorial(*_args); _args = []
    fact = t4
    print(fact)

if __name__ == '__main__':
    if 'main' in globals():
        main()