In this example, we create a Work Queue that will be used to distribute
time-consuming tasks among multiple workers.

The main idea behind Work Queues (aka: Task Queues) is to avoid doing a
resource-intensive task immediately and having to wait for it to complete.
Instead we schedule the task to be done later.
We encapsulate a task as a message and send it to the queue.
A worker process running in the background will pop the tasks and eventually execute the job.
When you run many workers the tasks will be shared between them.