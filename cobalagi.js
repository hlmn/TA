var kontol = [1, 2, 3, 4, 5];

function isBelowThreshold(currentValue) {
  if( currentValue === 2 ) return 'kontol';
}
function a(){
	// if(true) return console.log('kontol');
	for(i=0; kontol.length; i++){
		if (i==2) return 'kontol';
	}
	// console.log(kontol.every(isBelowThreshold))
}

console.log(a());
// console.log(a());



