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
