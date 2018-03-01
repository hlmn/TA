const { exec, spawn } = require('child_process');
const parseSentence = require('minimist-string');
var stringArgv = require('string-argv');
var net = require('net');
let checkMySQL, ls;
const isPortAvailable = require('is-port-available');
var port = 3306;
var knex = require('knex')({
  client: 'mysql2',
  // connection: {
  //   host: 'localhost',
  // 	user: 'root',

  // 	password: 'liverpoolfc'
  //   // database : 'myapp_test'
  // }
});
var forEach = require('async-foreach').forEach;
const knexQuery = require('knex')({
  client: 'mysql2',
  connection: {
    host: 'localhost',
  	user: 'root',
  	password: 'liverpoolfc',
  	database: 'mmt-its'
    // database : 'myapp_test'
  }
});

var moment = require('moment-timezone');
var amqp = require('amqplib');
var Promise = require("bluebird");
var PythonShell = require('python-shell');
var app = require('express')();
var server = require('http').Server(app);
var io = require('socket.io')(server);
server.listen(9999);
var redis = require("redis")
let redisClient;
var bluebird = require("bluebird");
bluebird.promisifyAll(redis.RedisClient.prototype);
bluebird.promisifyAll(redis.Multi.prototype);
let pattern;
var mysql      = require('mysql');
var client = {};
var ruanganlist = {};
var counter = 0;
app.post('/', function (req, res) {
  res.send('hello')

});
// test()

io.on('connection', function (socket) {

  //nunjukin id dari socketnya
  // socket.emit('worker', 'a');
  console.log(socket.id+' connected');

  socket.on('disconnect', function () {
  	// console.log(client[socket.id])
    console.log(socket.id+' disconnected');
    // console.log('ini' + Object.keys(client));
    if(typeof client[socket.id] === 'undefined') console.log('a');
    else{
    	delete ruanganlist[client[socket.id]].splice(ruanganlist[client[socket.id]].indexOf(socket.id), 1);
	    if (typeof ruanganlist[client[socket.id]][0] === 'undefined') delete ruanganlist[client[socket.id]];
	   	delete client[socket.id];
	   	console.log(client);
	   	console.log(ruanganlist);
    }
    


  });
  socket.on('mobile', function(msg){
    console.log(msg);
  });
  // socket.on('jalaninworker', function(msg){
  //   // if(workerFlag === 0){
  //   //   workerSpawn();
  //   //   console.log('Jalanin workerFlag')
  //   // }
  //   worker = spawn('python', [__dirname+'/worker.py']);
  //   console.log('worker masukin ke laravel dari socket on jalaninworker')
  // });

  socket.on('connected', function(){
  	console.log('a');
  });
  socket.on('id', function (msg){
  	client[socket.id] = msg;
  	if (typeof ruanganlist[msg] !== 'undefined') {
	  ruanganlist[msg].push(socket.id);
	}
	else ruanganlist[msg] = [socket.id];

  	console.log(client);
  	console.log(ruanganlist);
  });
});
function check(){
	function errorCallback(client){
		client.on('error', function (error) {
			console.error('> Re-connecting lost MySQL connection: ' + error);
			console.log(error.code)
			handleDisconnect(client);
		});		
	}
	function handleDisconnect(client) {
		mysqlClient = mysql.createConnection(client.config);
		setTimeout(function(){
			mysqlClient.connect(function(err) {
			  	if (err) {
			  		console.log(err.code)
				    console.error('error connecting: ' + err);			    
					handleDisconnect(mysqlClient);
					return;
				}
				tes()
				mysqlClient.destroy()
				console.log('connected as id ' + mysqlClient.threadId);
			});
		},2000)
	};
	var mysqlClient = mysql.createConnection({
	 	host: 'localhost',
	  	user: 'root',
	  	password: 'liverpoolfc'
	});
	mysqlClient.connect(function(err) {
	  	if (err) {
		    console.error('error connecting: ' + err);
		    handleDisconnect(mysqlClient);
			return;
		}
		tes()
		mysqlClient.destroy()
		console.log('connected as id ' + mysqlClient.threadId);
	});
}
function isJson(str) {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
}



let getPattern = () => {

	return new Promise( (resolve, reject) => {
		py = exec("python pattern.py", (error, stdout, stderr) => {
			if (error) {
				reject(`exec error: ${error}`);
				return;
			}
			if(isJson(stdout.toString())){
				result = JSON.parse(stdout.toString());
				resolve(result);
			} else {
				reject('bukan json');
			}
		});

	})
}
let buildQuery = (ptrn) => { 	
	return new Promise( (resolve, reject) => {
		Promise.each(Object.keys(ptrn) , (item, index, length) => {
			var pattern = []
			return Promise.each(ptrn[item]['pattern'], (item2, index2, length2) => {
				if(length2 != 1) var query = knex.distinct(item2[0]+'.'+ptrn[item]['ref'][index2][item2[1]]['referenced_column_name']).select().from(item);
				else var query = knex.distinct(item2[0]+'.'+ptrn[item]['ref'][index2][item]['referenced_column_name']).select(item2[0]+'.'+ptrn[item]['ref'][index2][item]['referenced_column_name']).from(item);
				item2.reverse();
				if(item2.length == 1) query.innerJoin(
							ptrn[item]['ref'][index2][item]['referenced_table_name'], 
							ptrn[item]['ref'][index2][item]['table_name']+'.'+ptrn[item]['ref'][index2][item]['column_name'], 
							ptrn[item]['ref'][index2][item]['referenced_table_name']+'.'+ptrn[item]['ref'][index2][item]['referenced_column_name']
						)
				else query.innerJoin(
							ptrn[item]['ref'][index2][item]['table_name'], 
							ptrn[item]['ref'][index2][item]['table_name']+'.'+ptrn[item]['ref'][index2][item]['column_name'], 
							ptrn[item]['ref'][index2][item]['referenced_table_name']+'.'+ptrn[item]['ref'][index2][item]['referenced_column_name']
						)
				return Promise.each(item2, (item3, index3, length3) =>{
					if(index3 < length3-1) query.innerJoin(
							item2[index3+1], 
							ptrn[item]['ref'][index2][item3]['table_name']+'.'+ptrn[item]['ref'][index2][item3]['column_name'], 
							ptrn[item]['ref'][index2][item3]['referenced_table_name']+'.'+ptrn[item]['ref'][index2][item3]['referenced_column_name']
						)
				}).then(() =>{
					pattern.push(query)
				});				
			}).then(() =>{
				ptrn[item]['query']= pattern 
			});
		}).then(() =>{
			resolve(ptrn)
		})
		.catch(() => {
			reject('error')
		});
	});
}

var promiseToFuckYou = function(data) {
	return new Promise( (resolve, reject) => {
		resolve(data)
	});
};
var brpopQueue = function() {
	
	var buildWhere  = (item, table, data) => {
		return new Promise((resolve, reject) => {
			queryResult = item.clone()			
			return Promise.each(Object.keys(data), (item1, index1, length1) => {
					queryResult.where(table+'.'+item1, data[item1]);
				}).then(() => {
					tes = queryResult.clone()
					console.log(tes.toString())
					queryResult.client = knexQuery.client;
					return queryResult
				}).then((q) => {
					resolve(q)
				}).catch((err) => {
					reject(err)
				})
		})
	}
	var getRuangan = function(table, query, data) {
		return new Promise((resolve, reject) => {
			var ruangan = [];
			function allDone(notAborted, arr) {
				ruangan = ruangan.reduce((x, y) => x.includes(y) ? x : [...x, y], [])
				console.log(ruangan)
				resolve(ruangan)
			}
			forEach(query, function(item, index, arr) {
				var done = this.async();
				buildWhere(item, table, data).then((res) => {
					forEach(res, function(item1, index1, arr1) {
						var done1 = this.async()
						ruangan.push(item1[Object.keys(item1)[0]]);
						done1();
					})
					done();
				})
				.catch((err) => {
					reject(err)
				});
			}, allDone);
		})
	}
	var sendMessage = (pesan, destination) => {
		return new Promise((resolve, reject) => {
			return amqp.connect('amqp://localhost').then(function(conn) {
			  return conn.createChannel().then(function(ch) {
			    var ex = destination;
			    var ok = ch.assertExchange(ex, 'fanout', {durable: true})
			    return ok.then(function() {
			      ch.publish(ex, '', Buffer.from(JSON.stringify(pesan)));
			      // console.log(pesan)
			      // console.log(" [x] Sent '%s'", pesan);
			      // ch.close();
			      return [pesan, ch.close()]
			    });
			  }).spread((msg, ch) => {
			  		return ch
			  }
			  ).finally(function() {
				  	conn.close()
				  	resolve(pesan)
			  }).catch((err) => {
			  	reject(err)
			  });
			}).catch(() => reject(console.warn));				
		})
	}
	console.log('waiting msg')
	redisClient.brpopAsync('maxwell', 0).then((data) => {
		// console.log('We have retrieved the data from the front of the queue:', data);
		log = data[1]
		if(isJson(log)){
			console.log(log)
			log = JSON.parse(log)
			// console.log(log['table']+' :')
			return [getRuangan(log['table'], pattern[log['table']]['query'], log['data']), log]
		}
	})
	.spread((data, log) => {
		function allDone(notAborted, arr) {
			redisClient.lpushAsync('logs', JSON.stringify(log)).then((res) => {
				console.log('log was saved to redis')
				brpopQueue()
			})
		}
		if(data.length > 0){
			forEach(data, function (item, index, arr){
				var done = this.async()
				sendMessage(log, item).then((res) => {
					console.log(JSON.stringify(res)+' sent to '+ item)
					done();
				}).catch((err) => {
					redisClient.rpushAsync('maxwell', item).then((res) => {

					})

				})
			}, allDone)
		}
		else allDone(null, null)
	})
	.catch((err) => {
		console.log(err)
	})
};

var initRedis = function(){
	redisClient = redis.createClient({
	  enable_offline_queue:false,
	  function (options) {
	        return 1000
	    }
	});
	redisClient.on('error', () =>{
		console.log('goblok')
	})
	redisClient.on('ready', () => {
		brpopQueue();
	})
}



function tes(){
	// ls = spawn("maxwell/bin/maxwell --user='root' --password='liverpoolfc' --host='127.0.0.1' --producer='redis' --output_binlog_position=true --config='maxwell/bin/config.properties'", [], { shell: true, encoding: 'utf-8' });

	ls = spawn("maxwell/bin/maxwell --user='root' --password='liverpoolfc' --host='127.0.0.1' --producer='redis' --output_binlog_position=true --config='maxwell/bin/config.properties'", [], { shell: true, encoding: 'utf-8' });
	// ls = spawn("maxwell/bin/maxwell --user='root' --password='liverpoolfc' --host='127.0.0.1' --producer='stdout' --output_binlog_position=true", [], { shell: true, encoding: 'utf-8' });
	ls.stdout.on('data', (data) => {
		// var string = data.toString().split('\n')
		// Promise.each(string, (item, index, length ) => {
		// 	if(isJson(item)) {
		// 		obj = JSON.parse(item);
		// 		position = obj['position'].split(':');
		// 		// console.log(item)
		// 		// sendMessage(item).then(() => console.log(item))
		// 		// sendMessage(item)
		// 		console.log(item)
		// 		redisClient.rpushAsync(position[0], item).then((data) => {
		// 			// knex.
		// 			// console.log(pattern)
		// 			console.log(item)
		// 			io.emit('kirim', item);
		// 		})
		// 		// .catch((err) => {
		// 		// 	console.log(err)
		// 		// })	
		// 	}
		// })
	  	console.log(`${data}`);
	});
	ls.stderr.on('data', (data) => {
	  	console.log(`${data}`);
	});
	ls.on('close', (code) => {
		console.log(`ea ${code}`);
		check();
	});
	process.on('SIGINT', function () {
		ls.on('close', (code) => {
			ls.kill();
			console.log(counter);
			process.exit(0);
		});
	});
}


getPattern().then((result) => {
	// console.log(result)
	return buildQuery(result)
})
.then((finalResult) => {
	pattern = finalResult;
	initRedis()
	console.log('query builded')
	tes();
})
.catch((err) => {
	console.log(err)
})
// tes();

