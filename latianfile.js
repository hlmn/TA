var fs = require('fs');
fs.writeFile("ip.txt", "Hey there!", function(err) {
    if(err) {
        return console.log(err);
    }

    console.log("The file was saved!");
}); 