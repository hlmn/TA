var redis = require("redis")
let redisClient;
var bluebird = require("bluebird");
bluebird.promisifyAll(redis.RedisClient.prototype);
bluebird.promisifyAll(redis.Multi.prototype);

var initRedis = function(){
	redisClient = redis.createClient({
	  enable_offline_queue:false,
	  function (options) {
	        return 1000
	    }
	});
	redisClient.on('error', () =>{
		console.log('redis dc')
	})
	redisClient.on('ready', () => {
		brpopQueue();
	})
}

var brpopQueue = function (){
	redisClient.brpopAsync('kontol', 0)
	.then((data) => {
		console.log(data)
		return redisClient.lpushAsync('kontol', data)
	})
	.then((data)=> {
		brpopQueue()
	})
}

initRedis()