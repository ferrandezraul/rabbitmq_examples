import pika
import sys

# Connect to broker
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))


channel = connection.channel()

# Create queue that does not loose messages (durable)
channel.queue_declare(queue='task_queue', durable=True)

# get message from given arguments or use hello world
message = ' '.join(sys.argv[1:]) or "Hello World!"


channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=2,  # make message persistent
    ))

print(" [x] Sent %r" % message)

connection.close()