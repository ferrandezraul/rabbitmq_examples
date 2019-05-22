from time import sleep

import pika


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


# Connect to the broker in localhost
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Use if exist or create queue "Hello"
channel.queue_declare(queue='hello')

# Tell rabbitmq to use the callback function in case a message arrives at queue "Hello"
channel.basic_consume(queue='hello',
                      auto_ack=True,
                      on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
