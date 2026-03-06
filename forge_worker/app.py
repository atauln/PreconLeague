import redis as r

redis_client = r.Redis(host='localhost', port=6379, db=0)

# on startup, we want to clear the queue
redis_client.delete('forge_queue')

# on shutdown, we want to clear the queue
def shutdown():
    redis_client.delete('forge_queue')

import atexit
atexit.register(shutdown)

# we want to listen to the queue and process tasks
while True:
    task = redis_client.blpop('forge_queue')
    if task:
        # process the task
        print(f'Processing task: {task[1]}')