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
					// console.log(item2)
					// console.log(item2[0]+'.'+ptrn[item]['ref'][index2][item]['referenced_column_name'])
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
			return amqp.connect('amqp://localhost').then(function(conn) {
			  return conn.createChannel().then(function(ch) {
			    var ex = destination;
			    var ok = ch.assertExchange(ex, 'fanout', {durable: true})
			    return ok.then(function() {
			      ch.publish(ex, '', Buffer.from(JSON.stringify(pesan)), {persistent: true});
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
			  	console.log('ga kekirik')
			  	reject(err)
			  });
			}).catch(() => {
				console.log('ga kekirik')
				reject(console.warn)
			});				
		})
	}

	var getAllRuangan = () => {
		return new Promise((resolve, reject) => {
			var ruangan = []
			knexQuery.select('id_kelas').from('kelas')
			.then((data) => {
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

					function checkPatternDone(notAborted, arr) {
						// console.log(ruangan)
						function allDone(notAborted, arr) {
							// console.log(ruangan)
							// resolve(data)
							
							selesai()
						}
						if (counter === 0){
							// console.log(data)
							selesai()
						}
						
						else {
							// if(res.length > 0){
							forEach(pattern[res[0]['referenced_table_name']]['query'], function(item1, index1, length1) {
								// console.log('a')
								var query = item1.clone()
								var done1 = this.async();
								query.where(res[0]['referenced_table_name']+'.'+res[0]['referenced_column_name'], old[item])
								console.log(query.toString())
								// console.log(knexQuery.client)
								query.client = knexQuery.client
								query.then((row) => {
									console.log(row.length)
									// row.map((x) => {
									// 	if (!data.includes(x['id_kelas']))data.push(x['id_kelas'])
									// })
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
									
									// console.log(data)
									
								})
							}, allDone)
							// }
							// else selesai()
							// else {
							// 	resolve(data)
							// }
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
	// var log;
	// redisClientBlocking.brpopAsync('maxwell', 0)
	redisClient.rpoplpushAsync('failed', 'failed').then((res) =>{
		if (res === null){
			// console.log('a')
			console.log('failed is empty, waiting msg')
			return redisClientBlocking.brpopAsync('maxwell', 0)
		} 
		else {
			// console.log(res)
			return res
		}
	})
	.then((res) => {
		// console.log(res)
		// process.exit(0)
		if (Array.isArray(res)){
			log = res[1]
		}
		else {
		var log = res;
			isFailed = true;
		}
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
		console.log('kontol')
		if(log['type'] === 'update'){
			if(Object.keys(log['old']).includes('id_kelas')){
				data.push(log['old']['id_kelas'])
				// console.log(data)
			}
		}
		
		function allDone(notAborted, arr) {
			// console.log(JSON.stringify(log))
			if(notAborted !== false)
				redisClient.lpushAsync('logs', JSON.stringify(log)).then((res) => {
					return redisClient.rpop('failed')
				})
				.then((res) => {
					brpopQueue()
				})
			else{
				console.log('a')
				brpopQueue()
			}
		}
		if(log['database'] !== 'mmt-its') allDone(null, null)
		else {
			if(data.length > 0){
				forEach(data, function (item, index, arr){
					var done = this.async()
					sendMessage(log, item).then((res) => {
						console.log(JSON.stringify(res)+' sent to '+ item)
						done();
					})
					.catch((err) => {
						// console.log('asoy');
						console.log(err)
						// done(false);
						// brpopQueue()
						done(false)
						// if(isFailed)
						// 	redisClient.rpushAsync('failed', JSON.stringify(log)).then((res) => {
						// 		done(false);
						// 	})
						// else 
						// 	redisClient.lpushAsync('failed', JSON.stringify(log)).then((res) => {
						// 		done(false);
						// 	})						
					})
				}, allDone)
			}
			else allDone(null, null)
		}
	})
	.catch((err) => {
		console.log(err)
		// console.log('error')
		brpopQueue()
		// if(log !== 'undefined'){
		// 	if(isFailed)
		// 		redisClient.rpushAsync('failed', JSON.stringify(log)).then((res) => {
		// 			brpopQueue()
		// 		});
		// 	else 
		// 		redisClient.lpushAsync('failed', JSON.stringify(log)).then((res) => {
		// 			brpopQueue()
		// 		});
		// }
		
	});
};
function tes(){
	// ls = spawn("maxwell/bin/maxwell --user='root' --password='semarmesem' --host='127.0.0.1' --producer='redis' --output_binlog_position=true --config='maxwell/bin/config.properties'", [], { shell: true, encoding: 'utf-8' });
	var ls = spawn("maxwell/bin/maxwell --user='root' --password='semarmesem' --host='127.0.0.1' --include_dbs='mmt-its' --exclude_tables=kelas --producer='redis' --output_binlog_position=true --config='maxwell/bin/config.properties'", [], { shell: true, encoding: 'utf-8' });
	// ls = spawn("maxwell/bin/maxwell --user='root' --password='semarmesem' --host='127.0.0.1' --producer='stdout' --output_binlog_position=true", [], { shell: true, encoding: 'utf-8' });
	ls.stdout.on('data', (data) => {
	  	console.log(`${data}`);
	});
	ls.stderr.on('data', (data) => {
	  	console.log(`${data}`);
	});
	ls.on('close', (code) => {
		console.log(`ea ${code}`);
		// delete ls
		check();
	});
	redisClient.on('error', () =>{
		console.log('redis dc')
		ls.kill()
		// ls.on('close', (code) => {
		// 	ls.kill();
			// console.log(counter);
		// });
	})
 // 	callback = () => {
	// 	ls.on('close', (code) => {
	// 		console.log('kontol')

	// 		ls.kill();
	// 		console.log(counter);
	// 		process.exit(0);
	// 	});
 // 	}
	// exitHook(callback => {
	// 	console.log('a')
	//     callback()
	// });
	process.on('SIGINT', function () {
		ls.on('close', (code) => {
			// console.log('kontol')

			ls.kill();
			console.log(counter);
			process.exit(0);
		});
	});
}
var initRedis = function(){
	redisClient = redis.createClient({
	  enable_offline_queue:true,
	  function (options) {
	        return 1000
	    }
	});
	redisClient.on('error', () =>{
		console.log('redis dc')
		
		// ls.on('close', (code) => {
		// 	ls.kill();
			// console.log(counter);
		// });
	})
	redisClientBlocking = redisClient.duplicate();
	redisClient.on('ready', () => {
		knexQuery = require('knex')({
		  client: 'mysql2',
		  connection: {
		    host: 'localhost',
		  	user: 'root',
		  	password: 'semarmesem',
		  	database: 'mmt-its'
		  }
		});
		brpopQueue();
		tes();
	})
	// redisClientBlocking.on('ready', () =>{
	// 	brpopQueue();
	// })

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
				  	password: 'semarmesem',
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
	  	password: 'semarmesem'
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
		  	password: 'semarmesem',
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

