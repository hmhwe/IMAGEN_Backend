#python imports
import os
import time
import picasconfig
import json

#picas imports
from picasclient.picas.actors import RunActor
from picasclient.picas.clients import CouchDB
from picasclient.picas.iterators import TaskViewIterator
from picasclient.picas.iterators import EndlessViewIterator
from picasclient.picas.iterators import PrioritizedViewIterator
from picasclient.picas.modifiers import BasicTokenModifier
from picasclient.picas.executers import execute
from picasclient.picas.util import Timer

class Actor(RunActor):
    
    def __init__(self, db, modifier, view1 = "highPriority", view2 = "lowPriority", **viewargs):
        super(Actor, self).__init__(db, None, view1=view1, **viewargs)
        self.timer = Timer()
        self.iterator = PrioritizedViewIterator(db, view1, view2, **viewargs) # overwrite default iterator from super().init()
        self.modifier = modifier
        self.client = db
        
        
        self.script_mapping = {
            "YOLOv5": "./yolov5.sh",
            "Video_Synchronization": "./data_cleaning.sh",
            # Add mappings here 
        }
        
       

    def handle_task_completion(self, token, out):
        
        # Get the job exit code in the token
        token['exit_code'] = out[0]
        token = self.modifier.close(token)
             
        # Attach logs in the token
        curdate = time.strftime("%d/%m/%Y_%H:%M:%S_")
       
        try:
            logsout = "logs_" + str(token['_id']) + ".out"
            log_handle = open(logsout, 'rb')
            token.put_attachment(logsout, log_handle.read())
        
            logserr = "logs_" + str(token['_id']) + ".err"
            log_handle = open(logserr, 'rb')
            token.put_attachment(logserr, log_handle.read())
       
        except:
            pass  
          
        
        
   
    def process_yolov5_task(self, token, task_type):
        
        task = self.script_mapping[task_type]       
        command = f"/usr/bin/time -v {task} \"{token['WEIGHTS']}\" \"{token['IMG']}\" {token['EPOCHS']} \"{token['DESTINATION_PATH']}\" 2> logs_" + str(token['_id']) + ".err 1> logs_" + str(token['_id']) + ".out"
        out = execute(command, shell=True)  
        
                          
        self.handle_task_completion(token, out)


    def process_cleaning_task(self, token, task_type):
        task = self.script_mapping[task_type]
        
        command = f"/usr/bin/time -v {task} \"{token['TestcastNumber']}\" 2> logs_" + str(token['_id']) + ".err 1> logs_" + str(token['_id']) + ".out"
        out = execute(command, shell=True)               
        
        self.handle_task_completion(token, out)

        
    def process_task(self, token):
        # Print token information
        print("-----------------------")
        print("Working on token: " + token['_id'])
        for key, value in token.doc.items():
            print(key, value)
        print("-----------------------")
    

    
        task_name = token['task_type']
        
        print(task_name)    
        
    
        
        if task_name == "YOLOv5":
            self.process_yolov5_task(token, task_name)
        elif task_name == "Video_Synchronization":
            self.process_cleaning_task(token, task_name)
        # Add more statements for other task types
        
       
            
            
         
    def time_elapsed(self, elapsed=30.):
        """
       @param elapsed: lifetime of the Actor in seconds

        @returns: bool
        """
        return self.timer.elapsed() > elapsed

     
        
        
        
def main():

    # setup connection to db
    client = CouchDB(url=picasconfig.PICAS_HOST_URL, db=picasconfig.PICAS_DATABASE, username=picasconfig.PICAS_USERNAME, password=picasconfig.PICAS_PASSWORD)
    print("Connected to the database %s sucessfully. Now starting work..." %(picasconfig.PICAS_DATABASE))
   
    # Create token modifier
    modifier = BasicTokenModifier()
    
    # Create actor
    actor = Actor(client, modifier, design_doc="Monitor_priority")
   
    # Start work!
    actor.run()
    
    print ("client exited") 

if __name__ == '__main__':
    main()