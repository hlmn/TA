var redis = require('redis'),
	redisClient = redis.createClient({
		function (options) {
	        // if (options.error && options.error.code === 'ECONNREFUSED') {
	        //     // End reconnecting on a specific error and flush all commands with
	        //     // a individual error
	        //     return new Error('The server refused the connection');
	        // }
	        // if (options.total_retry_time > 1000 * 60 * 60) {
	        //     // End reconnecting after a specific timeout and flush all commands
	        //     // with a individual error
	        //     return new Error('Retry time exhausted');
	        // }
	        // if (options.attempt > 10) {
	        //     // End reconnecting with built in error
	        //     return undefined;
	        // }
	        // reconnect after
	        return 1000
	        // return Math.min(options.attempt * 100, 3000);
	    }
	});
var bluebird = require("bluebird");
bluebird.promisifyAll(redis.RedisClient.prototype);
bluebird.promisifyAll(redis.Multi.prototype);



var brpopQueue = function() {
	console.log('waiting msg')
	redisClient.brpopAsync('maxwell', 0).then((data) => {
		console.log('We have retrieved the data from the front of the queue:', data);
	  	brpopQueue();
	}).catch((err) => {
		console.log('kontol')
	})
};

// redisClient.rpushAsync('adssa', 'dsadas').then((data) => {
// 	console.log(data)
// })
redisClient.on('error', () =>{
	// blpopQueue();
	console.log('goblok')
})
redisClient.on('ready', () => {
	brpopQueue();
})



// var redis  = require('redis');

// var port   = process.env.REDIS_PORT || null;
// var host   = process.env.REDIS_HOST || null;
// var client = redis.createClient(port, host,{detect_buffers: true});

// client.rpush('dataQueue', 'A string of data')

// client.lpop('dataQueue', function(error, data){
//   if (error) { 

//     console.error('There has been an error:', error);
//     }
//   console.log('We have retrieved data from the front of the queue:', data);
// })