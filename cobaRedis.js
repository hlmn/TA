var redis = require("redis")
let redisClient
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
      // app.exit()
      console.log('exit')
    })
    redisClient.on('ready', () => {
      redisClient.getAsync('kontol').then((res) => {
          console.log(res)
      })
    })
    
}

initRedis()