import json
temp_check = 35
pi_check = 4

def data_check(cJson):
    if len(cJson['e']) == 2:
        if cJson['e'][1]['v'] < 35:
            return 1
        else:
            return 0
    if len(cJson['e']) == 4:
        if cJson['e'][1]['v'] < 4:
            return 1
        else:
            return 0 
