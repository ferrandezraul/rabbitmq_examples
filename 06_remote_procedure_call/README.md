In the second tutorial we learned how to use Work Queues to distribute time-consuming tasks 
among multiple workers.

But what if we need to run a function on a remote computer and wait for the result? 
Well, that's a different story. This pattern is commonly known as Remote Procedure Call or RPC.

In this tutorial we're going to use RabbitMQ to build an RPC system: 
a client and a scalable RPC server. As we don't have any time-consuming tasks 
that are worth distributing, we're going to create a dummy RPC service that returns 
Fibonacci numbers.

#Client interface

To illustrate how an RPC service could be used we're going to create a simple client class. 
It's going to expose a method named call which sends an RPC request and blocks until 
the answer is received:


#A note on RPC

Although RPC is a pretty common pattern in computing, it's often criticised. 
The problems arise when a programmer is not aware whether a function call is local or 
if it's a slow RPC. 
Confusions like that result in an unpredictable system and adds unnecessary complexity to debugging. 
Instead of simplifying software, misused RPC can result in unmaintainable spaghetti code.

Bearing that in mind, consider the following advice:

+ Make sure it's obvious which function call is local and which is remote.
+ Document your system. Make the dependencies between components clear.
+ Handle error cases. How should the client react when the RPC server is down for a long time?

When in doubt avoid RPC. If you can, you should use an asynchronous pipeline - 
instead of RPC-like blocking, results are asynchronously pushed to a next computation stage.

#Callback queue

In general doing RPC over RabbitMQ is easy. 
A client sends a request message and a server replies with a response message. 
In order to receive a response the client needs to send a 'callback' queue address with the request.

#Correlation id
In the method presented above we suggest creating a callback queue for every RPC request. 
That's pretty inefficient, but fortunately there is a better way - 
let's create a single callback queue per client.

That raises a new issue, having received a response in that queue it's not clear to 
which request the response belongs. That's when the correlation_id property is used. 
We're going to set it to a unique value for every request. 
Later, when we receive a message in the callback queue we'll look at this property, 
and based on that we'll be able to match a response with a request. 
If we see an unknown correlation_id value, we may safely discard the message - 
it doesn't belong to our requests.

You may ask, why should we ignore unknown messages in the callback queue, 
rather than failing with an error? It's due to a possibility of a race condition on the server side. 
Although unlikely, it is possible that the RPC server will die just after sending us the answer, 
but before sending an acknowledgment message for the request. 
If that happens, the restarted RPC server will process the request again. 
That's why on the client we must handle the duplicate responses gracefully, 
and the RPC should ideally be idempotent.

#Our RPC will work like this:

* When the Client starts up, it creates an anonymous exclusive callback queue.
* For an RPC request, the Client sends a message with two properties: reply_to, which is set to the callback queue and correlation_id, which is set to a unique value for every request.
* The request is sent to an rpc_queue queue.
* The RPC worker (aka: server) is waiting for requests on that queue. When a request appears, it does the job and sends a message with the result back to the Client, using the queue from the reply_to field.
* The client waits for data on the callback queue. When a message appears, it checks the correlation_id property. If it matches the value from the request it returns the response to the application.

The server code is rather straightforward:

* (4) As usual we start by establishing the connection and declaring the queue.
* (11) We declare our fibonacci function. It assumes only valid positive integer input. (Don't expect this one to work for big numbers, it's probably the slowest recursive implementation possible).
* (19) We declare a callback for basic_consume, the core of the RPC server. It's executed when the request is received. It does the work and sends the response back.
* (32) We might want to run more than one server process. In order to spread the load equally over multiple servers we need to set the prefetch_count setting.

The client code is slightly more involved:

* (7) We establish a connection, channel and declare an exclusive 'callback' queue for replies.
* (16) We subscribe to the 'callback' queue, so that we can receive RPC responses.
* (18) The 'on_response' callback executed on every response is doing a very simple job, for every response message it checks if the correlation_id is the one we're looking for. If so, it saves the response in self.response and breaks the consuming loop.
* (23) Next, we define our main call method - it does the actual RPC request.
* (24) In this method, first we generate a unique correlation_id number and save it - the 'on_response' callback function will use this value to catch the appropriate response.
* (25) Next, we publish the request message, with two properties: reply_to and correlation_id.
* (32) At this point we can sit back and wait until the proper response arrives.
* (33) And finally we return the response back to the user.

The presented design is not the only possible implementation of a RPC service, but it has some important advantages:

* If the RPC server is too slow, you can scale up by just running another one. Try running a second rpc_server.py in a new console.
* On the client side, the RPC requires sending and receiving only one message. No synchronous calls like queue_declare are required. As a result the RPC client needs only one network round trip for a single RPC request.

Our code is still pretty simplistic and doesn't try to solve more complex (but important) problems, like:

* How should the client react if there are no servers running?
* Should a client have some kind of timeout for the RPC?
* If the server malfunctions and raises an exception, should it be forwarded to the client?
* Protecting against invalid incoming messages (eg checking bounds) before processing.

```
If you want to experiment, you may find the management UI useful for viewing the queues.
```