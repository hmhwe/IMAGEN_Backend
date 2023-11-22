import couchdb
from couchdb.design import ViewDefinition
import picasconfig


def createViews(db):
    generalViewCode='''
function(doc) {
   if(doc.type == "token") {
    if(%s) {
      emit(doc._id, doc._id);
    }
  }
}
'''
    # highpriority View
    highpriorityCondition = 'doc.lock == 0 && doc.done == 0 && doc.priority == 1'
    highpriority_view = ViewDefinition('Monitor_priority', 'highPriority', generalViewCode %(highpriorityCondition))
    highpriority_view.sync(db)
   
    # lowpriority View
    lowpriorityCondition = 'doc.lock == 0 && doc.done == 0 && doc.priority == 0'
    lowpriority_view = ViewDefinition('Monitor_priority', 'lowPriority', generalViewCode %(lowpriorityCondition))
    lowpriority_view.sync(db)
   
   
    # locked View
    lockedCondition = 'doc.lock > 0 && doc.done == 0'
    locked_view = ViewDefinition('Monitor_priority', 'locked', generalViewCode %(lockedCondition))
    locked_view.sync(db)
    
    
    # done View
    doneCondition = 'doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) == 0'
    done_view = ViewDefinition('Monitor_priority', 'done', generalViewCode %(doneCondition))
    done_view.sync(db)
    
    
    # error View
    errorCondition = 'doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) != 0'
    error_view = ViewDefinition('Monitor_priority', 'error', generalViewCode %(errorCondition))
    error_view.sync(db)
    
    
    # overview_total View -- lists all views and the number of tokens in each view
    overviewMapCode='''
function(doc) {
   if(doc.type == "token") {
       if (doc.lock == 0 && doc.done == 0){
          emit('todo', 1);
       }
       if(doc.lock > 0 && doc.done == 0) {
          emit('locked', 1);
       }
       if(doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) == 0) {
          emit('done', 1);
       }
       if(doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) != 0) {
          emit('error', 1);
       }
   }
}
'''
    overviewReduceCode='''
function (key, values, rereduce) {
   return sum(values);
}
'''
    overview_total_view = ViewDefinition('Monitor_priority', 'overview_total', overviewMapCode, overviewReduceCode)
    overview_total_view.sync(db)


def get_db():
    server = couchdb.Server(picasconfig.PICAS_HOST_URL)
    username = picasconfig.PICAS_USERNAME
    pwd = picasconfig.PICAS_PASSWORD
    server.resource.credentials = (username, pwd)
    db = server[picasconfig.PICAS_DATABASE]
    return db


if __name__ == '__main__':
    # Create a connection to the server
    db = get_db()
    # Create the Views in database
    createViews(db)