function enums(start,end,callback) {
   callback(start);
   if (end == 1)
      return 1;
   else{
      return enums(start + 1, end - 1, callback);
   }
}

var callback = function (number){
  console.log(number);
}
enums(1,10,callback);
// function(){ console.log("Rick"); }
setTimeout(function(){ console.log("Rick"); }, 0);