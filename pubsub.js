// var redis = require("redis")
// let redisClient;
// var bluebird = require("bluebird");
// bluebird.promisifyAll(redis.RedisClient.prototype);
// bluebird.promisifyAll(redis.Multi.prototype);

// redisClient = redis.createClient({
//   enable_offline_queue:true,
//   function (options) {
//         return 1000
//     }
// });
// redisClient.on('error', () =>{
// 	console.log('redis dc')

// })
// redisClient.on('ready', () => {
// 	redisClient.rpopAsync('anjing').then((data) => {
// 		console.log(data[1])
// 	})
// 	.catch((err)=>{
// 		console.log('dsdas')
// 	})
// })

// {"database":"mmt-its","table":"kode_kelas","type":"update","ts":1521698026,"xid":12388,"commit":true,"position":"master.000037:168225","data":{"id_kode_kelas":"d","kode_kelas":"a","created_at":null,"updated_at":null},"old":{"kode_kelas":"e"}}

// {"database":"mmt-its","table":"kode_kelas","type":"update","ts":1521698026,"xid":12388,"commit":true,"position":"master.000037:168225","data":{"id_kode_kelas":"E","kode_kelas":"a","created_at":null,"updated_at":null},"old":{"kode_kelas":"D"}}

a =  false
if (a === false)
	console.log("b" === "b")
else console.log('null')