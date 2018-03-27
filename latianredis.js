var redis = require("redis")
let redisClient;
var bluebird = require("bluebird");
bluebird.promisifyAll(redis.RedisClient.prototype);
bluebird.promisifyAll(redis.Multi.prototype);
redisClient = redis.createClient({
  enable_offline_queue:true,
  function (options) {
        return 1000
    },
   // retry_unfulfilled_commands : true
});
redisClient.on('error', () =>{
	console.log('redis dc')
})
redisClient.on('ready', () => {
	brpop()
})
var brpop = () => {
	// console.log('wait')
	redisClient.brpoplpushAsync('ea', 'tolol', 0).then((data) => {
		console.log(data);
		brpop();
	});
}
// brpop()