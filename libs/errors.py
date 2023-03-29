from merry import Merry

merry = Merry()


@merry._except(IOError)
def ioerror():
    print('Error: can\'t write to file')

@merry._except(Exception)
def catch_all(e):
    print('Unexpected error: ' + str(e))
