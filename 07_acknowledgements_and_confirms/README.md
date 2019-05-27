# Consumer Acknowledgements and Publisher confirms

Examples from https://www.rabbitmq.com/confirms.html

# Introduction
This guide covers two related features, consumer Acknowledgements 
and publisher confirms, **that are important for data safety** 
in applications that use messaging.

Systems that use a messaging broker such as RabbitMQ are 
by definition distributed. Since protocol methods (messages) sent are 
not guaranteed to reach the peer or be successfully processed by it,
both publishers and consumers need a mechanism for delivery and 
processing confirmation. Several messaging protocols supported 
by RabbitMQ provide such features. 
This guide covers the features in AMQP 0-9-1 but the idea is largely 
the same in other protocols (STOMP, MQTT, etcetera).

Delivery processing acknowledgements from consumers to RabbitMQ 
are known as acknowledgements in AMQP 0-9-1 parlance; 
broker acknowledgements to publishers are a protocol extension 
called publisher confirms.

Both features build on the same idea and are inspired by TCP. 
They are essential for reliable delivery both from publishers 
to RabbitMQ nodes and from RabbitMQ nodes to consumers.

# (Consumer) Delivery Acknowledgements
When RabbitMQ delivers a message to a consumer, it needs to know when 
to consider the message to be successfully sent. 
What kind of logic is optimal depends on the system. 
It is therefore primarily an application decision. 
In AMQP 0-9-1 it is made when a consumer is registered using the basic.consume method 
or a message is fetched on demand with the basic.get method.

If you prefer a more example-oriented and step-by-step material, 
consumer acknowledgements are also covered in RabbitMQ tutorial #2. (02_distribute_work)

# Delivery Identifiers: Delivery Tags
Before we proceed to discuss other topics it is important to explain 
how deliveries are identified (and acknowledgements indicate their 
respective deliveries). When a consumer (subscription) is registered, 
messages will be delivered (pushed) by RabbitMQ using the basic.deliver 
method. The method carries a delivery tag, which uniquely identifies the 
delivery on a channel. Delivery tags are therefore scoped per channel.

Delivery tags are monotonically growing positive integers and are 
presented as such by client libraries. 
Client library methods that acknowledge deliveries take a delivery 
tag as an argument.

Because delivery tags are scoped per channel, 
deliveries must be acknowledged on the same channel they were received on. 
Acknowledging on a different channel will result in an 
"unknown delivery tag" protocol exception and close the channel.

# Consumer Acknowledgement Modes and Data Safety Considerations
When a node delivers a message to a consumer, 
it has to decide whether the message should be considered handled 
(or at least received) by the consumer. 
Since multiple things (client connections, consumer apps, and so on) 
can fail, this decision is a data safety concern. 
Messaging protocols usually provide a confirmation mechanism 
that allows consumers to acknowledge deliveries to the node they 
are connected to. Whether the mechanism is used is decided at the 
time consumer subscribes.

Depending on the acknowledgement mode used, 
RabbitMQ can consider a message to be successfully delivered 
either immediately after it is sent out (written to a TCP socket) 
or when an explicit ("manual") client acknowledgement is received. 
Manually sent acknowledgements can be positive or negative and use 
one of the following protocol methods:

+ basic.ack is used for positive acknowledgements
+ basic.nack is used for negative acknowledgements (note: this is a RabbitMQ extension to AMQP 0-9-1)
+ basic.reject is used for negative acknowledgements but has one limitation compared to basic.nack

How these methods are exposed in client library APIs will be discussed below.
Positive acknowledgements simply instruct RabbitMQ to record a message 
as delivered and can be discarded. 
Negative acknowledgements with basic.reject have the same effect. 
The difference is primarily in the semantics: 
positive acknowledgements assume a message was successfully processed 
while their negative counterpart suggests that a delivery wasn't processed 
but still should be deleted.

In automatic acknowledgement mode, a message is considered to be successfully 
delivered immediately after it is sent. 
This mode trades off higher throughput (as long as the consumers can keep up) 
for reduced safety of delivery and consumer processing. 
This mode is often referred to as "fire-and-forget". 
Unlike with manual acknowledgement model, if consumers's TCP connection 
or channel is closed before successful delivery, the message sent by 
the server will be lost. Therefore, automatic message acknowledgement 
should be considered unsafe and not suitable for all workloads.

Another things that's important to consider when using automatic 
acknowledgement mode is that of consumer overload. 
Manual acknowledgement mode is typically used with a bounded channel 
prefetch which limits the number of outstanding ("in progress") 
deliveries on a channel. With automatic acknowledgements, however, 
there is no such limit by definition. 
Consumers therefore can be overwhelmed by the rate of deliveries, 
potentially accumulating a backlog in memory and running out of heap 
or getting their process terminated by the OS. 
Some client libraries will apply TCP back pressure 
(stop reading from the socket until the backlog of unprocessed 
deliveries drops beyond a certain limit). 
Automatic acknolwedgement mode is therefore only recommended 
for consumers that can process deliveries efficiently and at a steady rate.

# Positively Acknowledging Deliveries
API methods used for delivery acknowledgement are usually exposed 
as operations on a channel in client libraries. 
Java client users will use Channel#basicAck and Channel#basicNack 
to perform a basic.ack and basic.nack, respectively. 

Here's a Java client examples that demonstrates a positive acknowledgement:

```java
// this example assumes an existing channel instance

boolean autoAck = false;
channel.basicConsume(queueName, autoAck, "a-consumer-tag",
     new DefaultConsumer(channel) {
         @Override
         public void handleDelivery(String consumerTag,
                                    Envelope envelope,
                                    AMQP.BasicProperties properties,
                                    byte[] body)
             throws IOException
         {
             long deliveryTag = envelope.getDeliveryTag();
             // positively acknowledge a single delivery, the message will
             // be discarded
             channel.basicAck(deliveryTag, false);
         }
     });
```     
# Acknowledging Multiple Deliveries at Once
Manual acknowledgements can be batched to reduce network traffic. 
This is done by setting the multiple field of acknowledgement methods 
(see above) to true. 
Note that basic.reject doesn't historically have the field and that's 
why basic.nack was introduced by RabbitMQ as a protocol extension.

When the multiple field is set to true, RabbitMQ will acknowledge all 
outstanding delivery tags up to and including the tag specified in the 
acknowledgement. 
Like everything else related to acknowledgements, 
this is scoped per channel. 
For example, given that there are delivery tags 5, 6, 7, 
and 8 unacknowledged on channel Ch, when an acknowledgement frame arrives 
on that channel with delivery_tag set to 8 and multiple set to true, 
all tags from 5 to 8 will be acknowledged. 
If multiple was set to false, deliveries 5, 6, and 7 would still be 
unacknowledged.

To acknowledge multiple deliveries with RabbitMQ Java client, 
pass true for the multiple parameter to Channel#basicAck:
```    
// this example assumes an existing channel instance

boolean autoAck = false;
channel.basicConsume(queueName, autoAck, "a-consumer-tag",
     new DefaultConsumer(channel) {
         @Override
         public void handleDelivery(String consumerTag,
                                    Envelope envelope,
                                    AMQP.BasicProperties properties,
                                    byte[] body)
             throws IOException
         {
             long deliveryTag = envelope.getDeliveryTag();
             // positively acknowledge all deliveries up to
             // this delivery tag
             channel.basicAck(deliveryTag, true);
         }
     });
```    

# Negative Acknowledgement and Requeuing of Deliveries