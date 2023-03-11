
// --- GLOBAL VARIABLES ---

const api_url = "http://ec2-54-74-190-189.eu-west-1.compute.amazonaws.com:5000/";
// const api_url = "http://127.0.0.1:5000/";
//
var winW = window.innerWidth;
var winH = window.innerHeight;

let prices = {
	"REPAIR":{
		"front_bumper_damage":435,
		"hood_damage":492,
		"front_fender_damage":330,
		"sidedoor_panel_damage":368,
		"roof_damage":418,
		"backdoor_panel_damage":370,
		"rear_bumper_damage":399,
		"rear_fender_damage":323,
		"runnigboard_damage":342,
		"pillar_damage":322
	},
	"REPLACE":{
		"front_bumper_damage":547,
		"hood_damage":711,
		"front_fender_damage":517,
		"sidedoor_panel_damage":688,
		"roof_damage":799,
		"backdoor_panel_damage":754,
		"rear_bumper_damage":631,
		"rear_fender_damage":588,
		"runnigboard_damage":499,
		"pillar_damage":476,
		"headlight_damage":195,
		"front_windscreen_damage":660,
		"sidemirror_damage":175,
		"sidedoor_window_damage":337,
		"rear_windscreen_damage":575,
		"taillight_damage":138,
	}
}


// --- INIT ---

window.onload = function() {

	var fileInput = document.getElementById('filesupload');
	var fileList = [];
	
	fileInput.addEventListener('change', function (evnt) {
		fileList = [];
		for (var i = 0; i < fileInput.files.length; i++) {
			fileList.push(fileInput.files[i]);
		}
		console.log(fileList);
		display_originals(fileList);
		predict_all(fileList)
	});


}

// --- FUNCTIONS

const RETRY_COUNT = 5;
async function fetchRetry(...args) {
	let count = RETRY_COUNT;
  	while(count > 0) {
    		try {
      			return await fetch(...args);
    		} catch(error) {
			console.error('error:', error)
		}
    		count -= 1;
  	}

	throw new Error(`Too many retries`);
}

function display_originals( files ){

	var div_original = document.getElementById('originals');
	div_original.innerHTML = ""

	let i = 0;
	for (var file of files){
		var img_thumb = document.createElement("img")
		img_thumb.id = "thumb"+i
		img_thumb.classList.add('thumb');
        	img_thumb.src=URL.createObjectURL(file);
		div_original.appendChild(img_thumb);

		var img_original = document.createElement("img")
		img_original.id = "original"+i
		img_original.classList.add('original');
        	img_original.src=URL.createObjectURL(file);
		div_original.appendChild(img_original);

		i++;
		
		console.log(file)
	}
}


function predict_all(files){
 	var div_results = document.getElementById('all_results');
	div_results.innerHTML = ""

	predict_dmg_loop(files, 0)
}

function predict_dmg_loop(files, index=0){
     	postPicture(index, files, "predict_damages", saveJson)
}

function predict_plate_loop(files, index=0){
     	postPicture(index, files, "predict_plate", saveJson)
}

function postPicture(index, files, action, callback) {

	console.log("postPictures:"+index+" / "+action)
   
	let formData = new FormData();
	formData.append("file", filesupload.files[index]);

	var myInit = {
		method: 'POST',
		headers: new Headers(),
	    	// cache: 'default',
	    	// mode: 'cors',
	    	body: formData
    	}

    	return fetchRetry( api_url+action, myInit )
    	.then( response => response.json() )
    	.then( json => callback(json, index, files, action) )
    	.catch( error => console.error('error:', error) );
}

let save_json = []
function saveJson(json, index, files, action){
	console.log("saveJson:"+index+" / "+action+" / "+index+" / "+(files.length-1))

	switch(action){
		case "predict_damages":

			new_item = {
				'damages_json':json,
				'plates_json': null,
			}
			save_json[index] = new_item;

			predict_plate_loop(files, index)
			break;
		case "predict_plate":
			save_json[index]['plates_json'] = json
			showResult(save_json[index], index)

			if(index < files.length-1){
				predict_dmg_loop(files, index+1)
			} else {
				console.log("END")
				console.log(save_json)
			}
			break;
	}
}

function showResult( jsons, index ){

	var source = document.getElementById('blueprint')
	let new_element = source.cloneNode(true)
	new_element.id = "block"+index

 	var div_results = document.getElementById('all_results')
	div_results.appendChild(new_element)

	var canvas = new_element.getElementsByTagName("canvas")
    	ctx_dmg = canvas[0].getContext('2d')
	ctx_dmg.fillStyle = "#FF0000";
	ctx_dmg.fillRect(2, 2, 10, 10)
	newW = Math.min(winW/2,600)
 	drawCanvas(canvas[0], index, newW, newW, jsons);

	var result_cell = new_element.getElementsByClassName('result')
	addBullets(result_cell[0], jsons)

	var jsons_cell = new_element.getElementsByClassName('jsons')
	output_jsons = "<h3>Damages JSON</h3>"+JSON.stringify(jsons['damages_json'])
	output_jsons += "<hr><h3>Plates JSON</h3>"+JSON.stringify(jsons['plates_json'])
	jsons_cell[0].innerHTML = output_jsons
}

function addBullets(result_cell, jsons){

	var i = 0
 	for(let damage of jsons['damages_json'].damages){

		result = "<h3>Damage "+i+"</h3><ul>"
		for (const [key, value] of Object.entries(damage)) {
			if( ['action', 'severity', 'type'].includes(key) ){
				result += "<li><strong>"+key+":</strong> "+value+"</li>";
			}
		}

		result += "<li><strong>price:</strong> "+prices[damage['action']][damage['type']]+"$</li>";
		result += "</ul>"

		result_cell.innerHTML += result
		i++
	}

	i = 0
	for(let plate of jsons['plates_json'].plates){

		result = "<h3>Plate "+i+"</h3><ul>"
		for (const [key, value] of Object.entries(plate)) {
			if( ['text'].includes(key) ){
				result += "<li><strong>"+key+":</strong> "+value+"</li>";
			}
		}
		result += "</ul>"

		result_cell.innerHTML += result
		i++
	}
}

function drawCanvas(canvas, index, newWidth, newHeight, jsons) {


 	var image = document.getElementById('original'+index);

	canvas.width = newWidth;
        canvas.height = newHeight;

	ratioW = newWidth/image.width;
	ratioH = newHeight/image.height;

    	ctx = canvas.getContext('2d');

        // --- DRAW THE IMAGE
        ctx.drawImage(image, 0, 0, newWidth, newHeight);


	// --- DRAW DAMAGES 
 	colors = [
 		'#FF0000', // RED
 		'#0000FF', // BLUE
 		'#FF00FF', // MAGANTA
 		'#FFC000', // ORANGE
 		'#00CC00', // GREEN
 		'#FFFC00', // YELLOW
 		'#00FFFF', // CYAN
 	]
 
 
 	let i = 0
 	for(let damage of jsons['damages_json'].damages){
 
 		x = (damage.coords[0])*ratioW;
 		y = (damage.coords[1])*ratioH;
 		w = (damage.coords[2]-damage.coords[0])*ratioW;
 		h = (damage.coords[3]-damage.coords[1])*ratioH;
 
 		color = colors[i % colors.length]
 
 		ctx.beginPath();
 		ctx.rect(x, y, w, h)
 		ctx.strokeStyle = color;
 		ctx.stroke();
 
 		ctx.globalAlpha = 0.1;
 		ctx.fillStyle = "white";
 		ctx.fillRect(x, y, w, h);
 		ctx.globalAlpha = 1.0;
 
 		ctx.font = "10px Arial";
 		ctx.textAlign = "left";
 		txt = i+" "+damage.type;
 		let width = ctx.measureText(txt).width;
 
 		ctx.fillStyle = "white";
 		ctx.fillRect(x, y, width+10, 15);
 
 		ctx.fillStyle = color;
 		ctx.fillText(txt, x+5, y+10);
 		i++;
 	}

	// --- DRAW PLATES 
	i = 0

	ctx.lineWidth = 3;
	ctx.setLineDash([10, 5]);

	for(let plate of jsons['plates_json'].plates){

 		x = (plate.coords[0])*ratioW;
 		y = (plate.coords[1])*ratioH;
 		w = (plate.coords[2]-plate.coords[0])*ratioW;
 		h = (plate.coords[3]-plate.coords[1])*ratioH;

		color = "#FF0000"

		ctx.beginPath();
		ctx.rect(x, y, w, h)
		ctx.strokeStyle = color;
		ctx.stroke();

		i++;
	}
}
