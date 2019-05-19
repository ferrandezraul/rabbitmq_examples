import pika

# Connect to the broker in localhost
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Use if exist, or create, the queue named hello
channel.queue_declare(queue='hello')

# Publish a message "Hello World" to the hello queue
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')

# Print message that this client has sent "Hello World"s
print(" [x] Sent 'Hello World!'")




