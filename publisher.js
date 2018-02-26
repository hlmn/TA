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
  // 	database: 'goblok',
  // 	password: 'liverpoolfc'
  //   // database : 'myapp_test'
  // }
});
var Promise = require("bluebird");
var PythonShell = require('python-shell');
var app = require('express')();
var server = require('http').Server(app);
var io = require('socket.io')(server);
server.listen(9999);
var redis = require("redis"),
    redisClient = redis.createClient({
      enable_offline_queue:false,
    });
var bluebird = require("bluebird");
bluebird.promisifyAll(redis.RedisClient.prototype);
bluebird.promisifyAll(redis.Multi.prototype);
var pattern;
var mysql      = require('mysql');
var client = {};
var ruanganlist = {};
var counter = 0;
app.post('/', function (req, res) {
  res.send('hello')

});
// test()
// var kontol = [1, 2, 3, 4, 5]
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
				// errorCallback(mysqlClient)
				tes()
				mysqlClient.destroy()
				console.log('connected as id ' + mysqlClient.threadId);
			});
		},2000)
	};
	var mysqlClient = mysql.createConnection({
	 	host: 'localhost',
	  	user: 'root',
	  	// database: 'goblok',
	  	password: 'liverpoolfc'
	});
	// handleDisconnect(mysqlClient)
	// mysqlClient.connect()
	mysqlClient.connect(function(err) {
	  	if (err) {
		    console.error('error connecting: ' + err);
		    handleDisconnect(mysqlClient);
			return;
		}
		// errorCallback(mysqlClient)
		tes()
		mysqlClient.destroy()
		console.log('connected as id ' + mysqlClient.threadId);
	});
}
function isJson(str) {
    try {
        JSON.parse(str);
    } catch (e) {
    	// console.log()
        return false;
    }
    return true;
}

function anjing(str){
	++counter;
	knex('tes').insert({hilman: str})
		.then((id) => {
			console.log(id);
		})
	webServerPort.on('error', function(e) {
	});	// console.log(str)
}

let getPattern = () => {
	return new Promise( (resolve, reject) => {
		py = exec("python pattern.py", (error, stdout, stderr) => {
			if (error) {
				reject(`exec error: ${error}`);
				return;
			}
			// console.log(stdout.toString())
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
			// console.log(item+' :')
			var pattern = []
			return Promise.each(ptrn[item]['pattern'], (item2, index2, length2) => {
				// var query = knex.from(item);
				// console.log(query)
				if(length2 != 1)var query = knex.select(item2[0]+'.'+ptrn[item]['ref'][index2][item2[1]]['referenced_column_name']).from(item);
				else var query = knex.select(item2[0]+'.'+ptrn[item]['ref'][index2][item]['referenced_column_name']).from(item);
				item2.reverse();
				query.innerJoin(
							ptrn[item]['ref'][index2][item]['referenced_table_name'], 
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
				// console.log('NGENTOT')
			resolve(ptrn)
		})
		.catch(() => {
				reject('error')
		});
	});
}

function tes(){
	// ls = spawn("maxwell/bin/maxwell --user='root' --password='liverpoolfc' --host='127.0.0.1' --producer='redis' --exclude_dbs='goblok' --output_binlog_position=true --config='maxwell/bin/config.properties'", [], { shell: true, encoding: 'utf-8' });
	ls = spawn("maxwell/bin/maxwell --user='root' --password='liverpoolfc' --host='127.0.0.1' --producer='stdout' --exclude_dbs='goblok' --output_binlog_position=true", [], { shell: true, encoding: 'utf-8' });
	ls.stdout.on('data', (data) => {
		var string = data.toString().split('\n')
		string.forEach((item, index) => {
			if(isJson(item)) {
				obj = JSON.parse(item);
				position = obj['position'].split(':');
				redisClient.rpushAsync(position[0], item).then((data) => {
					// knex.
					// console.log(pattern)
					io.emit('kirim', item);
				})
				.catch((err) => {
					console.log(err)
				})	
			}
		})
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
	console.log('query builded')
	tes();
})
.catch((err) => {
	console.log(err)
})
// tes();

