import logging, datetime
from time import sleep
import threading, traceback


door_controller_mutex = threading.Lock()
event_log_mutex       = threading.Lock()

logger = logging.getLogger('Controller')

class Event():
    @staticmethod
    def get_time():
        return datetime.datetime.now()

    class Id_Read():
        def __init__(self, id):
            self.id = id
            self.timestamp = Event.get_time()

    class Id_Access_Accepted():
        def __init__(self, id, server_positive_reply):
            self.id = id
            self.timestamp = Event.get_time()
            self.server_reply = server_positive_reply

    class Id_Access_Rejected():
        def __init__(self, id, server_negative_reply):
            self.id = id
            self.timestamp = Event.get_time()
            self.server_reply = server_negative_reply

    class Server_Timeout():
        def __init__(self, id, ):
            self.id = id
            self.timestamp = Event.get_time()

    class Id_Allowed_In_Disconnect_State():
        pass

    class Id_Read_While_Busy():
        def __init__(self, id):
            self.id = id
            self.timestamp = Event.get_time()

class Event_Recorder():
    def __init__(self):
        self.events = []
    def record(self, event):
        self.events.append(event)


class Controller:
    def __init__(self):
        self.communication = None
        self.lock          = None
        self.reader        = None

        self.event_recorder = Event_Recorder()

    def add_event(self, event):
        event_log_mutex.acquire(True) #blocking acquire
        try:
            self.event_recorder.events.append(event)
        finally:
            event_log_mutex.release()

    def log_events(self):
        pass

    def save_offline_access(self):
        pass

    def load_offline_access(self):
        pass

    #this method gets called (async) by the reader every time a card is read
    def read(self, id):
        try:
            #a mutex because we only want to process one read card at a time
            if door_controller_mutex.acquire(False): #non-blocking acquire
                try:
                    logger.debug("ID {id} was read: processing".format(**locals()))
                    self.add_event(Event.Id_Read(id))

                    # we ask the server if we should open the door for the id - if the server timeouts, we open it anyways and log that fact
                    permission_request = self.communication.get_permission(id)

                    if permission_request.valid:
                        if permission_request.allow:
                            self.add_event(Event.Id_Access_Accepted(id, permission_request))
                            self.lock.open()
                        else:
                            self.add_event(Event.Id_Access_Rejected(id, permission_request))
                    else:
                        self.add_event(Event.Id_Allowed_In_Disconnect_State(id, permission_request))
                        self.lock.open()

                finally:
                    door_controller_mutex.release()
            else:
                self.add_event(Event.Id_Read_While_Busy(id))
                logger.debug("ID {id} was read but an earlier read is being processed".format(**locals()))

        except Exception as e:
            trace_stack = traceback.format_exc()
            logger.critical("Unrecoverable error has occurred: {0}".format(str(e)))
            logger.critical("{0}".format(trace_stack))

