In 02_distribute_work we created a work queue.
The assumption behind a work queue is that each task is delivered to exactly one worker.
In this part we'll do something completely different -- we'll deliver a message to multiple consumers.

This pattern is known as "publish/subscribe".

To illustrate the pattern, we're going to build a simple logging system.
It will consist of two programs -- the first will emit log messages and the second will receive and print them.

In our logging system every running copy of the receiver program will get the messages.
That way we'll be able to run one receiver and direct the logs to disk; and at the same time we'll be able to run
another receiver and see the logs on the screen.

Essentially, published log messages are going to be broadcast to all the receivers.

The core idea in the messaging model in RabbitMQ is that the producer never sends any messages directly to a queue. Actually, quite often the producer doesn't even know if a message will be delivered to any queue at all.

Instead, the producer can only send messages to an exchange.
An exchange is a very simple thing.
On one side it receives messages from producers and the other side it pushes them to queues.
The exchange must know exactly what to do with a message it receives.
Should it be appended to a particular queue?
Should it be appended to many queues?
Or should it get discarded.
The rules for that are defined by the exchange type.