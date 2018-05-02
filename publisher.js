const { exec, spawn } = require('child_process');
const parseSentence = require('minimist-string');
var stringArgv = require('string-argv');
var net = require('net');
let checkMySQL;
var port = 3306;
var knex = require('knex')({
  client: 'mysql2'
});
const exitHook = require('async-exit-hook');
var forEach = require('async-foreach').forEach;
let knexQuery, ls;
var moment = require('moment-timezone');
var amqp = require('amqplib');
var Promise = require("bluebird");
var PythonShell = require('python-shell');
// var app = require('express')();
// var server = require('http').Server(app);
// var io = require('socket.io')(server);
// server.listen(9999);
let rabbitMqConnection;
var redis = require("redis")
let redisClient, redisClientBlocking;
var bluebird = require("bluebird");
bluebird.promisifyAll(redis.RedisClient.prototype);
bluebird.promisifyAll(redis.Multi.prototype);
let pattern;
var mysql      = require('mysql');
var counter = 0;

let mysqlClient

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
		py = exec("python pattern-server.py", (error, stdout, stderr) => {
			if (error) {
				reject(`exec error: ${error}`);
				// reject('bukan json');
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
				if(item2.length != 1) {
					// console.log(item2[0]+'.'+ptrn[item]['ref'][index2][item2[1]]['referenced_column_name'])
					var query = knex.distinct(item2[0]+'.'+ptrn[item]['ref'][index2][item2[1]]['referenced_column_name']).select().from(item);
				}
				else{
					var query = knex.distinct(item2[0]+'.'+ptrn[item]['ref'][index2][item]['referenced_column_name']).select().from(item);
				} 
				item2.reverse();
				
				if(item == ptrn[item]['ref'][index2][item]['table_name']) query.innerJoin(
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
// var isFailed = false;
var brpopQueue = function() {
	
	var buildWhere  = (item, table, data) => {
		return new Promise((resolve, reject) => {
			queryResult = item.clone()			
			return Promise.each(Object.keys(data), (item1, index1, length1) => {
					queryResult.where(table+'.'+item1, data[item1]);
				}).then(() => {
					cloneQuery = queryResult.clone()
					console.log(cloneQuery.toString())
					queryResult.client = knexQuery.client;
					return queryResult
				}).then((q) => {
					console.log('aman')
					console.log(q)
					resolve(q)
				}).catch((err) => {
					reject(err)
				})
		})
	}
	var getRuangan = function(table, query, data) {
		// console.log(data)
		return new Promise((resolve, reject) => {
			var ruangan = [];
			function allDone(notAborted, arr) {
				ruangan = ruangan.reduce((x, y) => x.includes(y) ? x : [...x, y], [])
				// console.log(ruangan)
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
			var ex = destination;
			var ok = rabbitMqConnection.assertExchange(ex, 'fanout', {durable: true})
			return ok.then(function() {
				rabbitMqConnection.publish(ex, '', Buffer.from(JSON.stringify(pesan)), {persistent: true});
				// console.log(pesan)
				// console.log(" [x] Sent '%s'", pesan);
				// ch.close();
				return pesan
			}).then((pesan) => {
				resolve(pesan)
			}).catch((err) => {
				console.log('ga kekirim')
				reject(err)
			});
				
			// }).then(null, console.warn).catch(() => {
			// 	console.log('ga kekirim')
			// 	reject(console.warn)
			// });				
		})
	}

	var getAllRuangan = () => {
		return new Promise((resolve, reject) => {
			var ruangan = []
			knexQuery.select('id_kelas').from('kelas')
			.then((data) => {
				console.log('aman2')
				return Promise.each(data, (item, index, length) => {
					ruangan.push(item['id_kelas'])
				})
			})
			.then(() =>{
				resolve(ruangan)
			});
		})
	}
	var getOldRuangan = (data, log) => {
	// console.log(log)
		// data = []
		if(!Array.isArray(data))
			data = []

		return new Promise((resolve, reject) => {
			old = log['old']
			table = log['table']
			function oldDone(notAborted, arr){
				console.log(data)
				resolve(data)
			} 
			forEach(Object.keys(old), function (item, index, length) {
			// Object.keys(old).map(item => {
				var selesai = this.async()
				knexQuery.column('referenced_table_name', 'referenced_column_name').select().from('information_schema.key_column_usage').where({
					table_name : table,
					column_name : item,
					table_schema : 'mmt-its'
				})
				.then((res) => {
					// console.log(res)
					console.log(res)
					console.log('aman3')
					function checkPatternDone(notAborted, arr) {
						function allDone(notAborted, arr) {
							selesai()
						}
						if (counter === 0){
							selesai()
						}
						
						else {
							forEach(pattern[res[0]['referenced_table_name']]['query'], function(item1, index1, length1) {
								var query = item1.clone()
								var done1 = this.async();
								query.where(res[0]['referenced_table_name']+'.'+res[0]['referenced_column_name'], old[item])
								console.log(query.toString())
								query.client = knexQuery.client
								query.then((row) => {
									console.log('aman4')
									console.log(row.length)
									function selesaiPush(notAborted, arr){
										done1()
									}
									if(row.length > 0){
										forEach(row, function(item2, index2, length2) {
											var kelar = this.async()
											if (!data.includes(item2['id_kelas']))data.push(item2['id_kelas'])
											kelar()
										}, selesaiPush)
									}
									else done1()
									
								})
								.catch((err) => reject(err))
							}, allDone)
							
						}				
					}
					// var count = pattern[table]['pattern'].length
					var counter = 0
					if(res.length > 0){
						forEach(pattern[table]['pattern'], function(pattern, indexPattern, patternLength) {
							var done = this.async();
							if (pattern.includes(res[0]['referenced_table_name']) && res[0]['referenced_table_name'] !== 'kelas'){
								++counter
								console.log('asik')
							}
							done();						
						}, checkPatternDone)
					}
					else selesai()
						
					
					
				})
				.catch((err) => {
					reject(err)
				})
			}, oldDone)
			
		})
	}
	var writeToFile = (waktu) => {
		console.log(waktu)
		return new Promise( (resolve, reject) => {
			var check = require('fs'); 
			check.stat(__dirname+'/benchmark.txt', function(err, stat) {
				var fs = require('fs');
				if (err === null) { 
					fs.appendFile(__dirname+'/benchmark.txt', 'time : '+waktu+'\r\n', (err) => {
						if (err) reject(err);
						console.log(waktu)
						resolve(waktu)
					})
				}
				else if (err.code == 'ENOENT') {
					fs.writeFile(__dirname+'/benchmark.txt', 'time : '+waktu+'\r\n', (err) => {
						if (err) reject(err);
						console.log(waktu)						
						resolve(waktu)
					});
				}
			})
		});
	}
	var time;
	redisClient.rpoplpushAsync('failed', 'failed').then((res) =>{
		if (res === null){
			// console.log('a')
			console.log('there is no failed job, waiting new message')
			return redisClient.brpoplpushAsync('maxwell', 'failed', 0)
		} 
		else {
			// console.log(res)
			return res
		}
	})
	.then((res) => {
		time = new Date().getTime()/1000;
		var log = res;
		if(isJson(log)){
			console.log(log)
			log = JSON.parse(log)
			// console.log(pattern[log['table']])
			if(log['database'] === 'mmt-its') {
				if(log['type'] === 'delete')
					return [getAllRuangan(), log]
				else return [getRuangan(log['table'], pattern[log['table']]['query'], log['data'], log), log]
			}
			else return [[null], log]
		}
		else return [[null], log]
	})
	.spread((data, log) => {
		if(log['type'] === 'update'){
			return [getOldRuangan(data, log), log]
		}
		else return [data, log]
	})
	.spread((data, log) => {
		console.log(data)
		if(log['type'] === 'update'){
			if(Object.keys(log['old']).includes('id_kelas')){
				data.push(log['old']['id_kelas'])
			}
		}
		// console.log('anjay')
		function allDone(notAborted, arr) {
			if(notAborted !== false){
				var timeEnd = new Date().getTime()/1000
				redisClient.lpushAsync('logs', JSON.stringify(log))
				.then((res) => {
					return redisClient.rpop('failed')
				})
				.then((res) => {
					
					return writeToFile(timeEnd - time)
				})
				.then((res) => {
					console.log('\n')
					brpopQueue()
				})
			}
			else{
				brpopQueue()
			}
		}
		if(log['database'] !== 'mmt-its') allDone(null, null)
		else {
			console.log('ea')
			if(data.length > 0){
				forEach(data, function (item, index, arr){
					var done = this.async()
					sendMessage(log, item).then((res) => {
						
						console.log(JSON.stringify(res)+' sent to '+ item)
						done();
					})
					.catch((err) => {
						console.log(err)
						done(false)
						
					})
				}, allDone)
			}
			else allDone(null, null)
		}
	})
	.catch((err) => {
		console.log(err)
		brpopQueue()
		
	});
};
function tes(){
	ls = spawn("maxwell/bin/maxwell --user='root' --password='liverpoolfc' --host='127.0.0.1' --include_dbs='mmt-its' --exclude_tables=kelas,mesin_log  --producer='redis' --output_binlog_position=true --config='maxwell/bin/config.properties'", [], { shell: true, encoding: 'utf-8' });
	ls.stdout.on('data', (data) => {
		console.log(`${data}`);
	});
	ls.stderr.on('data', (data) => {
		console.log(`${data}`);
	});
	ls.on('close', (code) => {
		console.log(`ea ${code}`);
		check();
	});
	redisClient.on('error', () =>{
		console.log('redis dc')
		ls.kill()
	})
	process.on('SIGINT', function () {
		ls.on('close', (code) => {
			ls.kill();
			console.log(counter);
			process.exit(0);
		});
	});
}
var initRedis = function(){
	redisClient = redis.createClient({
	  enable_offline_queue:true,
	  retry_strategy: function (options) {
	        return 1000
	    }
	});
	redisClient.on('error', () =>{
		console.log('redis dc')
		redisClient = null
		// setTimeout(function() {
		// 	initRedis()
		// }, 0)
		
	})
	// redisClientBlocking = redisClient.duplicate();
	redisClient.on('ready', () => {
		knexQuery = require('knex')({
		  client: 'mysql2',
		  connection: {
		    host: 'localhost',
		  	user: 'root',
		  	password: 'liverpoolfc',
		  	database: 'mmt-its'
		  }
		});
		retryRmqConnection = () =>{
			if (rabbitMqConnection!==null)console.log('retry connection to rabbitMq')
			rabbitMq = amqp.connect('amqp://127.0.0.1:5672').then((conn) => {
			  	conn.createChannel().then((ch) => {
					rabbitMqConnection = ch
				})
				console.log('readyrabbit')
				conn.on('close', function(err){
				setTimeout( function() {
						retryRmqConnection()
					}, 0 );
				})
			}).catch( (err) => {
			  rabbitMqConnection = null
			  setTimeout( function() {
					  retryRmqConnection()
				  }, 0 );
			})
		}
		var rabbitMq = amqp.connect('amqp://127.0.0.1:5672').then((conn) => {
			
			conn.createChannel().then((ch) => {
				rabbitMqConnection = ch
			})
			brpopQueue();
			conn.on('close', function(err){
				retryRmqConnection()
			})
		}).catch((err)=>{
			console.log(err)
			retryRmqConnection()
		})
		tes();
	})
}
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
				if (redisClient.connected) {tes()}
				mysqlClient.destroy()
				knexQuery = require('knex')({
				  client: 'mysql2',
				  connection: {
				    host: 'localhost',
				  	user: 'root',
				  	password: 'liverpoolfc',
				  	database: 'mmt-its'
				  }
				});
				console.log('connected as id ' + mysqlClient.threadId);
			});
		},2000)
	};
	mysqlClient = mysql.createConnection({
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
		if (redisClient.connected) {tes()}
		mysqlClient.destroy()
		knexQuery = require('knex')({
		  client: 'mysql2',
		  connection: {
		    host: 'localhost',
		  	user: 'root',
		  	password: 'liverpoolfc',
		  	database: 'mmt-its'
		  }
		});

		console.log('connected as id ' + mysqlClient.threadId);
	});
}

var init = function(){
	getPattern().then((result) => {
	// console.log(result)
		return buildQuery(result)
	})
	.then((finalResult) => {
		pattern = finalResult;
		// console.log(pattern)
		initRedis()
		console.log('query builded')
		
	})
	.catch((err) => {
		// init()
		console.log('aa')
		console.log(err)
	})
}
init()
// tes();

