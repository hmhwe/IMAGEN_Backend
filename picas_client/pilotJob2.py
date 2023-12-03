import os
import time
import picasconfig
import json

from picas.actors import RunActor
from picas.clients import CouchDB
from picas.iterators import TaskViewIterator
from picas.iterators import EndlessViewIterator
from picas.modifiers import BasicTokenModifier
from picas.executers import execute
from picas.util import Timer

# Abstract base class for task processors
class TaskProcessor:
    def __init__(self, modifier):
        self.modifier = modifier
    def process_task(self, token):
        pass
        
        

# Task processor for YOLOv5 task
class YOLOv5Processor(TaskProcessor):
    def __init__(self, modifier):
        super().__init__(modifier)

    def process_task(self, token, task_script):
        # Print token information
        print("-----------------------")
        print("Working on token: " + token['_id'])
        for key, value in token.doc.items():
            print(key, value)
        print("-----------------------")
        
        
        
        command = f"/usr/bin/time -v {task_script} \"{token['WEIGHTS']}\" \"{token['IMG']}\" {token['EPOCHS']} \"{token['BATCH_SIZE']}\" 2> logs_" + str(token['_id']) + ".err 1> logs_" + str(token['_id']) + ".out"
        out = execute(command, shell=True)  
       
                          
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
          
          

# Task processor for Video Synchronization task
class VideoSynchronizationProcessor(TaskProcessor):
    def process_task(self, token, task_script):
        print("Processing Video Synchronization task:", token)
        # Implement VideoSynch here



# Task processor factory
class TaskProcessorFactory:
    def create_processor(self, task_type, modifier):
        if task_type == "YOLOv5":
            return YOLOv5Processor(modifier)
        elif task_type == "Video_Synchronization":
            return VideoSynchronizationProcessor(modifier)
        # Add more processors for other task types
        
      

#Tasks to script mapping
class TaskScriptMapper:
    def __init__(self):
        self.task_mapping = {
            "YOLOv5": "./scripts/yolov5.sh",
            "Video_Synchronization": "./scripts/data_cleaning.sh",
        }

    def get_task_script(self, task_type):
        return self.task_mapping.get(task_type, None)


# Actor class using the factory
class Actor(RunActor):
    def __init__(self, db, modifier, task_script_mapper,  view="todo", **viewargs):
        super(Actor, self).__init__(db, view=view, **viewargs)
        self.timer = Timer()
        self.iterator = EndlessViewIterator(self.iterator, stop_callback=self.time_elapsed)
        self.modifier = modifier
        self.client = db
        self.task_script_mapper = task_script_mapper
        self.processor_factory = TaskProcessorFactory()

    def process_task(self, token):
        task_type = token['task_type']
        task_script = self.task_script_mapper.get_task_script(task_type)

        if task_script:
            processor = self.processor_factory.create_processor(task_type, self.modifier)
            processor.process_task(token, task_script)
        else:
            print(f"No task script found for task type: {task_type}")

    def time_elapsed(self, elapsed=30.):
        return self.timer.elapsed() > elapsed


# Example of using the Actor
def main():
    client = CouchDB(url=picasconfig.PICAS_HOST_URL, db=picasconfig.PICAS_DATABASE,
                     username=picasconfig.PICAS_USERNAME, password=picasconfig.PICAS_PASSWORD)
    print("Connected to the database %s sucessfully. Now starting work..." %(picasconfig.PICAS_DATABASE))

    # Create token modifier
    modifier = BasicTokenModifier()

    # Create task script mapper
    task_script_mapper = TaskScriptMapper()

    # Create actor
    actor = Actor(client, modifier, task_script_mapper)

    # Start work!
    actor.run()

if __name__ == '__main__':
    main()