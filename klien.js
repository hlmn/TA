const socket = require('socket.io-client')('http://127.0.0.1:9999');
counter = 0;

socket.on('connect', () =>{
	console.log('konek boi');
})

socket.on('kirim', (data) => {
	console.log(data);
	counter = counter + 1;
	console.log(counter)
});

