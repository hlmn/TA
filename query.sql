select constraint_name, table_name, referenced_table_name from `information_schema`.key_column_usage where table_schema = 'mmt-its' and referenced_table_name is not null and (referenced_table_name = 'jadwal' or `table_name` = 'jadwal');


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

}

