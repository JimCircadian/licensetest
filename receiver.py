#!/usr/bin/env python

import sys
import asyncore
import email
import smtpd
import time
from threading import Thread

DEBUG = True

class CustomSMTPServer(smtpd.SMTPServer):
    num = 0
    
    def process_message(self, peer, mailfrom, recvtos, data):
        msg = email.message_from_string(data).get_payload().strip()
        self.num += 1
        
        if DEBUG:
            print >>sys.stderr, "DEBUG: Received message {0}".format(msg)
            
    def get_num(self):
        return self.num

class Receiver(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
    def start(self):
        self.smtp = CustomSMTPServer((self.host, self.port), None)
        self.thread = Thread(target = asyncore.loop, kwargs = {'timeout': 1})
        self.thread.daemon = True
        self.thread.start()
        
    def status(self):
        return "running" if self.thread.is_alive() else "stopped"
        
    def stop(self):
        self.smtp.close()
        self.thread.join()
        
    def get_received(self):
        return str(self.smtp.get_num())
        
if __name__ == "__main__":
    recv = Receiver("0.0.0.0", 2255)
    recv.start()
    
    print "HELLO - going to sleep but can receive messages"
    time.sleep(30)
    print "All done"
    
    recv.stop()
