We're going to add a feature to the exemple in 03_publish_and_subscribe -
we're going to make it possible to subscribe only to a subset of the messages.
For example, we will be able to direct only critical error messages to the log file (to save disk space),
while still being able to print all of the log messages on the console.

In 03_publish_and_subscribe, we were using a fanout exchange, which doesn't give us too much flexibility -
it's only capable of mindless broadcasting.

Now, we will use a direct exchange instead.
The routing algorithm behind a direct exchange is simple -
a message goes to the queues whose binding key exactly matches the routing key of the message.

If you want to save only 'warning' and 'error' (and not 'info') log messages to a file, just open a console and type:
```
python receive_logs_direct.py warning error > logs_from_rabbit.log
```
If you'd like to see all the log messages on your screen, open a new terminal and do:
```
python receive_logs_direct.py info warning error
# => [*] Waiting for logs. To exit press CTRL+C
```

And, for example, to emit an error log message just type:
```
python emit_log_direct.py error "Run. Run. Or it will explode."
# => [x] Sent 'error':'Run. Run. Or it will explode.'
```
