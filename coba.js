sysvar Q = require("q");

// create the connection to database
var knex = require('knex')({
  client: 'mysql2',
  connection: {
    host: 'db.muhammadhilman.com',
  	user: 'hlmn',
  	database: 'mmt-its',
  	password: 'liverpoolfc'
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

function kontol(table, fromTest){
	// // console.log(table);
	// if(table === null && fromTest === null) {
	// 	// console.log(fromTest)
	// 	// console.log('goblokbgt')
	// 	return 1;
	// }
	if(table === null && fromTest !== null) {
		console.log(fromTest)
		// console.log('goblokbgt')
		return 1;
	}
	/// else console.log(from);
	return knex.select('*')
		.from('INFORMATION_SCHEMA.KEY_COLUMN_USAGE')
		.where('TABLE_SCHEMA', 'mmt-its')
		.whereNotNull('REFERENCED_TABLE_NAME')
		.andWhere(function(){
			this.where('REFERENCED_TABLE_NAME', table).orWhere('TABLE_NAME', table)
		})
		.orderBy('table_name', 'asc')
		.then(rows => {

			var count = 0;
			for (var i = 0; i < rows.length; i++) {
				if(rows[i].REFERENCED_TABLE_NAME === table && rows[i].REFERENCED_TABLE_NAME !== table_master) ++count
			}
			if (rows.length !== count){
				if(fromTest === null)
					fromTest = [];
				// else fromTest.push(table);

				var fromRow = [];
				
				for (var i = 0; i < rows.length; i++) {
					fromRow[i] = fromTest;
					// console.log(rows[i])
					if(rows[i].REFERENCED_TABLE_NAME === table ){
						if(fromRow[i].includes(rows[i].REFERENCED_TABLE_NAME)){
							console.log('continue');
							// fromRow[i].push(rows[i].REFERENCED_TABLE_NAME);

							// console.log(fromRow[i])
							continue;
						}
						else{
							fromRow[i].push(rows[i].REFERENCED_TABLE_NAME);
							// console.log(fromRow)
							if(rows[i].REFERENCED_TABLE_NAME === table_master )			console.log('pindah ke '+rows[i].TABLE_NAME+' dari '+table_master);
							else console.log('pindah ke '+fromRow[i][fromRow[i].length-1]+' dari '+rows[i].TABLE_NAME);
							kontol(rows[i].TABLE_NAME, fromRow[i]);
						}
					}
					else{
						
						if(fromRow[i].includes(rows[i].REFERENCED_TABLE_NAME)) continue;
						else{
							// fromRow[i].push(rows[i].REFERENCED_TABLE_NAME);
							console.log(rows[i].REFERENCED_TABLE_NAME+" > "+ rows[i].TABLE_NAME);
							kontol(rows[i].REFERENCED_TABLE_NAME, fromRow[i]);
						}
						
		
					}
					// console.log(fromRow)
				}
				// return 1;
			}
			else {
				console.log('pucuk '+table)
				// from.push(table);
				// console.log(from)
				kontol(null, fromTest);
			}
			// return kontol(rows, table);
		});
	
}

kontol(table_master, null);


