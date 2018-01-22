// const mysql = require('mysql2');
var Q = require("q");

// create the connection to database
var knex = require('knex')({
  client: 'mysql2',
  connection: {
    host: 'localhost',
  	user: 'root',
  	database: 'mmt-its'
    // database : 'myapp_test'
  }
});
// const connection = mysql.createConnection({
//   host: 'localhost',
//   user: 'root',
//   database: 'mmt-its'
// });
var tabel = {};

const table_master = 'kelas';
var counter = 0;

function kontol(table, from, callback){
	// callback(table)555555445454545454545454545454545454545454434343
	// if(!table) return false;
	// else
	if(table === null) {
		console.log('goblokbgt')
		return 1;
	}
	return knex.select('*').from('INFORMATION_SCHEMA.KEY_COLUMN_USAGE').where('TABLE_SCHEMA', 'mmt-its').whereNotNull('REFERENCED_TABLE_NAME').andWhere(function(){
		this.where('REFERENCED_TABLE_NAME', table).orWhere('TABLE_NAME', table)
	})
	.then(rows => {
		var count = 0;
		for (var i = 0; i < rows.length; i++) {
			if(rows[i].REFERENCED_TABLE_NAME === table && rows[i].REFERENCED_TABLE_NAME !== table_master) ++count
		}
		if (rows.length !== count){
			for (var i = 0; i < rows.length; i++) {
					
				if(rows[i].REFERENCED_TABLE_NAME === table ){
					if(rows[i].TABLE_NAME === from ) continue;
					else{
						if(rows[i].REFERENCED_TABLE_NAME === table_master ) {
							// continue;
							// kontol(rows[i].TABLE_NAME, callback);
							console.log('init')
							 kontol(rows[i].TABLE_NAME, table_master, callback);
						}
						else {
							console.log('stopped at ' + rows[i].REFERENCED_TABLE_NAME + " for "+rows[i].TABLE_NAME+" from "+from)
							// return kontol(rows[i].TABLE_NAME, callback);
							// if()
							 kontol(rows[i].TABLE_NAME, rows[i].REFERENCED_TABLE_NAME ,callback);
						}
					}
					
					
					// kontol(rows[i].TABLE_NAME, callback);
				}
				else{
					if(rows[i].REFERENCED_TABLE_NAME === from) continue;
					else{
						console.log(rows[i].REFERENCED_TABLE_NAME+" > "+ rows[i].TABLE_NAME);
						 kontol(rows[i].REFERENCED_TABLE_NAME, rows[i].TABLE_NAME,callback);
					}
					
	
				}
			}
		}
		else {
				console.log('pucuk '+table)
				kontol(null, from, callback);
		}
		// return kontol(rows, table);
	});
	
}


var callback = function (rows,table){
	// console.log(rows)
	for (var i = 0; i < rows.length; i++) {
		if(rows[i].REFERENCED_TABLE_NAME == table){
			if(rows[i].REFERENCED_TABLE_NAME == table_master) {
				// continue;
				// kontol(rows[i].TABLE_NAME, callback);
				kontol(rows[i].TABLE_NAME, callback);
			}
			else kontol(rows[i].TABLE_NAME, callback);
			
			// kontol(rows[i].TABLE_NAME, callback);
		}
		else{
			console.log(rows[i].REFERENCED_TABLE_NAME+">"+table);
			kontol(rows[i].REFERENCED_TABLE_NAME, callback);

		}
	}
	// return 1;
	// rows.forEach(function(key, item){
	// 	kontol(item.table_name, callback);
	// });
}


console.log(kontol(table_master, null, callback));
// .then(function(rows){
// 	console.log(rows);
// })
// connection.query(
//   'SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = "mmt-its"',
//   function(err, results, fields) {
//   	// console.log(results)
//   	results.forEach(function(element){
//   		tabel[element.TABLE_NAME] = 0
//   	})
  	
//   	connection.query(
// 	  'SELECT `TABLE_SCHEMA`, `TABLE_NAME`, `COLUMN_NAME`, `REFERENCED_TABLE_SCHEMA`, `REFERENCED_TABLE_NAME`, `REFERENCED_COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`KEY_COLUMN_USAGE` WHERE `TABLE_SCHEMA` = SCHEMA() AND `REFERENCED_TABLE_NAME` IS NOT NULL and REFERENCED_TABLE_NAME = "kelas"',
// 	  function(err, results, fields) {
// 	  	results.forEach(function(element){
// 	  		kontol(element.TABLE_NAME)
// 	  	})
// 	    // console.log(results[0].TABLE_SCHEMA); // results contains rows returned by server
// 	    // console.log(fields); // fields contains extra meta data about results, if available
// 	  }
// 	);
//     // console.log(results[0].TABLE_SCHEMA); // results contains rows returned by server
//     // console.log(fields); // fields contains extra meta data about results, if available
//   }
// );
// simple query



