#!/usr/bin/env python

import sys
import pprint
import smtplib
import time
import uuid

from email.mime.text import MIMEText
from threading import Thread, Event

DEBUG = True

class Sender():
    # TODO: Private, underscore
    args = None
    db = {}
    dur = 10
    emails = 10

    def __init__(self, host, port):
        self.init_db()
        self.host = host
        self.port = port
        self.stopped = Event()
        self.thread = Thread(target = self.send)
        self.thread.daemon = True

    def send(self):
        delay = self.dur / self.emails
        
        while not self.stopped.wait(delay):
            avail = filter(lambda x: not x[1]['sent'], self.db.items())
        
            if len(avail) > 0:
                (ident, det) = avail.pop()
                msg = det['msg']

                if DEBUG:
                    print >>sys.stderr, "DEBUG: Sending email {0}".format(ident)

                try:
                    sender = smtplib.SMTP(self.host, self.port)
                    sender.sendmail(msg['From'], msg['To'], msg.as_string())
                    sender.quit()
                    if DEBUG:
                        print >>sys.stderr, "SEND SUCCESS: {0}".format(ident)
                    self.db[ident]['sent'] = True
                except:
                    if DEBUG:
                        print >>sys.stderr, "SEND FAILURE: {0}".format(ident)

    def duration(self, d): 
        sent = len(filter(lambda x: x['sent'], self.db.values()))
        
        if sent > 0:
            return False
            
        try:
            self.dur = int(d)
        except:
            raise ValueError("What the hell is this: {0} of type {1}".format(d, type(d)))
        return True
        
    def get_db(self):
        return self.db
        
    def get_duration(self):
        return self.dur
        
    def get_from(self):
        return 'james.byrne@linuxit.com'

    def get_limit(self):
        return str(len(self.db.items()))
        
    def get_sent(self):
        return str(len(filter(lambda x: x[1]['sent'], self.db.items())))
        
    def get_subject(self, ident):
        return "Generated test email {0}".format(ident)

    def get_to(self):
        return 'james.byrne@linuxit.com'

    def init_db(self, num = 0):
        while num < self.emails:
            key = format(uuid.uuid4())

            msg = MIMEText(key)
            msg['From'] = self.get_from()
            msg['To'] = self.get_to()
            msg['Subject'] = self.get_subject(num)

            value = {
                'msg':      msg,
                'sent':     False,
                'received': False,
            }
            num += 1
            self.db[key] = value
    
    def limit(self, msgs):
        sent = len(filter(lambda x: x['sent'], self.db.values()))
        num = len(self.db.values())
        
        if sent > 0:
            return False
            
        try:
            if int(msgs) > self.emails:
                self.emails = int(msgs)
                self.init_db(num)
            elif int(msgs) < self.emails:
                newdb = { k: self.db[k] for k in self.db.keys()[0:int(msgs)] }
                self.db = newdb
        except:
            raise ValueError("What the hell is this: {0} of type {1}".format(msgs, type(msgs)))
        return True
        
#        if msgs < len(lambda x: x['sent'], self.db):
#            # TODO: Set message feedback
#            return 
#            
#        
#        # TODO: stop sending and reset db to new limit
#        self.emails = msgs
        
    def running(self): 
        return not self.stopped.is_set()        
    
    def start(self):
        self.thread.start()
        
    def status(self):
        return "running" if self.thread.is_alive() else "stopped"
        
    def stop(self):
        self.stopped.set()

if __name__ == "__main__":
    s = Sender('localhost', 2255)
    s.start()
    while s.running():
        print "DEBUG: Waiting for sends to finish {0}".format(len(filter(lambda e: not e['sent'], s.get_db().values())))
        time.sleep(2)
        if len(filter(lambda e: not e['sent'], s.get_db().values())) == 0:
            s.stop()
