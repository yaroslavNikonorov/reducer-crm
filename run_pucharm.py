import sys

from manage import main

if __name__ == '__main__':
    sys.argv[0] = "manage.py"
    sys.argv.append("import_models")
    """./manage.py import_models /home/yar/Downloads/Spool_models_import\ -\ Sheet1.csv"""
    sys.argv.append("/home/yar/Downloads/Spool_models_import.csv")
    print(sys.argv)
    main()
