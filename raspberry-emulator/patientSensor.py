

class PatientSensor :
    def __init__(self) :
        pass

    def emulateData(self) :
        #print('testSensor')
        self.fp = open('test.txt','w')
        self.fp.write('test')
        self.fp.close()