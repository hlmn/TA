const { spawn } = require('child_process');
const parseSentence = require('minimist-string');
var stringArgv = require('string-argv');
var net = require('net');
let checkMySQL, ls;
const isPortAvailable = require('is-port-available');
 
var port = 3306;
var knex = require('knex')({
  client: 'mysql2',
  connection: {
    host: 'localhost',
  	user: 'root',
  	database: 'goblok',
  	password: 'liverpoolfc'
    // database : 'myapp_test'
  }
});
// test()
// var kontol = [1, 2, 3, 4, 5]
function check(){
	checkMySQL = new net.Socket();	
	checkMySQL.connect(3306, '127.0.0.1');
    checkMySQL.setKeepAlive(true);
	checkMySQL.on('connect', function(){
		console.log('kontol')
	})
}
function isJson(str) {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
}
var counter = 0;
function anjing(str){
	++counter;
	knex('tes').insert({hilman: str})
		.then((id) => {
			console.log(id);
		})
	// console.log(str)

}
function tes(){
	ls = spawn("maxwell/bin/maxwell --user='root' --password='liverpoolfc' --host='127.0.0.1' --producer='stdout' --exclude_dbs='goblok'", [], { shell: true, encoding: 'utf-8' });
	ls.stdout.on('data', (data) => {
		// kontol.forEach(function(index, item){
		// 	setTimeout(function(){
		// 		++counter;
		// 	},1000);
		// });
		if(isJson(`${data}`)){

		} 

		var string = data.toString().split('\n')
		// for(i = 0; i < string.length; i++){
		// 	if(isJson(string[i])) {
		// 		setTimeout(function(){					
		// 			anjing(string[i])
		// 		}, 2000)
								
		// 	}
		// }
		string.forEach((item, index) => {
			if(isJson(item)) {
				setTimeout(function(){
					++counter;
					knex('tes').insert({hilman: item}).then((id) => {
						console.log(id);
					});		
				}, 2000)
					
			}
			// console.log('ea:'+item)
		})
		// console.log();
	  	
	});
	ls.stderr.on('data', (data) => {
	  	// console.log(`oo${data}`);
	});
	ls.on('close', (code) => {
		console.log(`ea ${code}`);
	});
	process.on('SIGINT', function () {
		ls.on('close', (code) => {
			ls.kill();
			console.log(counter);
			process.exit(0);
		});
	});
}
// check()
tes();

