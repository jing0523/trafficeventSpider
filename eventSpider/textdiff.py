from twisted.internet import task
from twisted.internet import reactor

def runEverySecond():
    print "60 seconds has passed"

l = task.LoopingCall(runEverySecond)
l.start(60) # call every second

# l.stop() will stop the looping calls
reactor.run()