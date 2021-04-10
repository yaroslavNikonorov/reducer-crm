import sys

from manage import main

if __name__ == '__main__':
    sys.argv[0] = "manage.py"
    sys.argv.append("runserver")
    print(sys.argv)
    main()
