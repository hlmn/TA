#!/usr/bin/env node

var amqp = require('amqplib');

// amqp.connect('amqp://localhost', function(err, conn) {
//   conn.createChannel(function(err, ch) {
//     var ex = 'coy';

//     ch.assertExchange(ex, 'fanout', {durable: true});

//     ch.assertQueue('c', {exclusive: false}, function(err, q) {
//       console.log(" [*] Waiting for messages in %s. To exit press CTRL+C", q.queue);
//       ch.bindQueue(q.queue, ex, '');

//       ch.consume(q.queue, function(msg) {
//         console.log(" [x] %s", msg.content.toString());
//       }, {noAck: true});
//     });
//   });
// });


amqp.connect('amqp://localhost').then(function(conn) {
  process.once('SIGINT', function() { conn.close(); });
  return conn.createChannel().then(function(ch) {
    var ok = ch.assertExchange('logs', 'fanout', {durable: true});
    ok = ok.then(function() {
      return ch.assertQueue('dasdsaaa', {exclusive: false});
    });
    ok = ok.then(function(qok) {
      return ch.bindQueue(qok.queue, 'logs', '').then(function() {
        return qok.queue;
      });
    });
    ok = ok.then(function(queue) {
      return ch.consume(queue, logMessage, {noAck: true});
    });
    return ok.then(function() {
      console.log(' [*] Waiting for logs. To exit press CTRL+C');
    });

    function logMessage(msg) {
      console.log(" [x] '%s'", msg.content.toString());
    }
  });
}).catch(console.warn);