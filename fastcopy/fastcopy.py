import time
import threading

read_unit = 1024*1024 * 16
data_list_max = 4

class ReadThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.cond_not_full = threading.Condition(self.lock)
        self.cond_not_empty = threading.Condition(self.lock)
        self.data_list = []
        self.fd = None

    def destroy(self):
        self.fd.close()

    def start( self, filename ):
        self.fd = open( filename, "rb" )
        threading.Thread.start(self)

    def run(self):

        self.lock.acquire()
            
        while True:

            while len(self.data_list) >= data_list_max:
                self.cond_not_full.wait()
            
            self.lock.release()
            data = self.fd.read(read_unit)
            self.lock.acquire()

            self.data_list.append(data)

            self.cond_not_empty.notify()

            if not data:
                break

        self.lock.release()

    def getData(self):

        self.lock.acquire()
            
        while len(self.data_list) == 0:
            self.cond_not_empty.wait()
        
        data = self.data_list[0]
        del self.data_list[0]

        self.cond_not_full.notify()

        self.lock.release()
        
        return data

def test_multithreaded():

    fd = open( "./dst1.bin", "wb" )

    read_thread = ReadThread()
    read_thread.start( "./src1.bin" )
    
    while True:
        data = read_thread.getData()
        if not data:
            break
        fd.write(data)

    read_thread.join()
    read_thread.destroy()

    fd.close()

def test_singlethread():

    fd = open( "./dst2.bin", "wb" )
    fd_src = open( "./src2.bin", "rb" )

    while True:
        data = fd_src.read(read_unit)
        if not data:
            break
        fd.write(data)

    fd_src.close()
    fd.close()

print "unit", read_unit

t1 = time.time()
test_multithreaded()
t2 = time.time()
print "multi-threaded  :", t2-t1

t1 = time.time()
test_singlethread()
t2 = time.time()
print "single-threaded :", t2-t1


"""
unit 67108864
multi-threaded  : 37.8789999485
single-threaded : 48.1070001125

unit 33554432
multi-threaded  : 32.0450000763
single-threaded : 39.2649998665

unit 16777216
multi-threaded  : 19.2000000477
single-threaded : 27.2650001049

unit 8388608
multi-threaded  : 25.0529999733
single-threaded : 36.0979998112

unit 4194304
multi-threaded  : 30.368999958
single-threaded : 30.6649999619

unit 2097152
multi-threaded  : 37.248000145
single-threaded : 38.2149999142

unit 1048576
multi-threaded  : 42.9739999771
single-threaded : 45.7630000114

unit 524288
multi-threaded  : 45.3020000458
single-threaded : 52.1399998665

unit 262144
multi-threaded  : 47.5130000114
single-threaded : 52.2969999313

"""
