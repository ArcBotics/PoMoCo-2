import wx
import threading, os, time
import Queue

class Note():
    def __init__(self):
        self.sender = ""
        self.receiver = ""
        self.type = ""
        self.message = ""

class Node(threading.Thread):

    modules = {}
    
    def __init__(self):
        self.inNoteQueue = Queue.Queue()
        self.moduleType = ""
        self.NoteTypes  = []

    def sendNote(self, note):
        Node.modules[note.receiver].put(note)
        #print self.moduleType,"Sent Note:",note.sender,"->",note.receiver,"-",note.type,":",note.message

    def writeAndSendNote(self, type, message, receiver):
        toSend = Note()
        toSend.sender = self.moduleType
        toSend.type = type
        toSend.message = message
        toSend.receiver = receiver
        self.sendNote(toSend)
        
    def processNote(self, note):
        pass
    
    def addNote(self, note):
        print self.inNoteQueue
        self.inNoteQueue.put(note)
    
    def run(self):
        while True:
            try:
                message = self.inNoteQueue.get(block=False)
                self.processNote(message)
            except Queue.Empty: 
                pass
            time.sleep(0) # keeps infinite loop from hogging all the CPU