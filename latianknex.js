var Promise = require("bluebird");
var knexQuery = require('knex')({
  client: 'mysql2',
  connection: {
    host: 'localhost',
  	user: 'root',
  	password: 'liverpoolfc',
  	database: 'mmt-its'
  }
});
var knexQueryBuild = require('knex')({
  client: 'mysql2',
});

var getOldRuangan = (data, log) => {
	// console.log(log)
	return new Promise((resolve, reject) => {
		old = log['old']
		table = log['table']
		return Promise.each(Object.keys(old), (item, index, length) => {
			knexQuery.column('referenced_table_name', 'referenced_column_name').select().from('information_schema.key_column_usage').where({
				table_name : table,
				column_name : item,
				table_schema : 'mmt-its'
			})
			.then((res) => {
				if(data.length > 0){
					Promise.each(pattern[table]['query'], (item1, index1, length1) => {
						query.item
					})
				}
				
			})
		})
		// .then((data) =>
		// 	console.log('b')
		// )
		// .then((data) => {
		// 	console.log('x')
		// })
	})
}
log = JSON.parse('{"database":"mmt-its","table":"absen","type":"update","ts":1522058810,"xid":3825,"commit":true,"position":"master.000016:332540","data":{"id_absen":"dsadas","id_kartu":null,"id_jadwal":"13faab2f-34f3-47ff-a172-8cbb5f8bcd6ac","waktu_absen":"2018-03-26 17:06:50","nrp":"5111540000005"},"old":{"id_jadwal":"13faab2f-34f3-47ff-a172-8cbb5f8bcd6a","waktu_absen":"2018-03-26 17:04:14"}}')

getOldRuangan([], log)