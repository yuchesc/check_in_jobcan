import sys
from jobcan import Jobcan


if __name__ == '__main__':
    try:
        comment = input()
        if comment == '':
            raise Exception('Need comment.')

        jobcan = Jobcan()
        jobcan.checkout(sys.argv[1], sys.argv[2])
    except Exception as e:
        print(e)
        sys.exit(1)
