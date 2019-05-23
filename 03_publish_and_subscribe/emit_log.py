import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

# After establishing the connection we declared the exchange.
# This step is necessary as publishing to a non-existing exchange is forbidden.
channel.exchange_declare(exchange='logs', exchange_type='fanout')

message = ' '.join(sys.argv[1:]) or "info: Hello World!"

# We need to supply a routing_key when sending, but its value is ignored for fanout exchanges.
# cause in fanout we broadcast to every channel connected to it.
# The messages will be lost if no queue is bound to the exchange yet,
# but that's okay for us; if no consumer is listening yet we can safely discard the message.
channel.basic_publish(exchange='logs', routing_key='', body=message)

print(" [x] Sent %r" % message)

connection.close()