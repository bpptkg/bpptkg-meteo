import threading
import time


def worker():
    print('Worker started.')
    time.sleep(5)
    print('Worker finished.')


def main():
    print('Main started.')

    i = 0
    while True:
        print(i)
        if i % 5 == 0:
            print('Starting worker thread')
            t = threading.Thread(target=worker, args=())
            t.start()
            print('Ending worker thread.')
        time.sleep(1)

        i += 1

    print('Main finished.')


if __name__ == '__main__':
    main()
