from core.controller import PluggitController

if __name__ == '__main__':
    try:
        app = PluggitController()
    except KeyboardInterrupt as e:
        print 'Goodbye!'
        exit(-1)
