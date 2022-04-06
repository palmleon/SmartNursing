from datetime import datetime
import time

def isNightTime(timestamp):
    nightTime = [21,7]
    date_received = datetime.fromtimestamp(timestamp)
    print(date_received)
    if date_received.hour >= nightTime[0] or date_received.hour <= nightTime[1]:
        return True
    else:
        return False

def hasAdayPassed(timestamp):
    latestBtReceived = datetime.fromtimestamp(timestamp)
    now = datetime.fromtimestamp(time.time())
    if now.day > latestBtReceived.day or now.month > latestBtReceived.month or now.year > latestBtReceived.year:
        return True
    else:
        return False


if __name__ == '__main__':
    print(isNightTime(1649192033))
    print(hasAdayPassed(1649105633))
    print(hasAdayPassed(1649192033))
    
