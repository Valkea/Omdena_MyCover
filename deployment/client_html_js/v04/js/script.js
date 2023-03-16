
// --- GLOBAL VARIABLES ---

const api_url = "http://ec2-54-74-190-189.eu-west-1.compute.amazonaws.com:5000/";
//const api_url = "http://127.0.0.1:5000/";

var winW = window.innerWidth;
var winH = window.innerHeight;

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
		initializeCells(fileList);
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
		var name = file.name

		var img_thumb = document.createElement("img")
		img_thumb.id = "thumb_"+name;
		img_thumb.classList.add('thumb');
        	img_thumb.src=URL.createObjectURL(file);
		div_original.appendChild(img_thumb);

		var img_original = document.createElement("img")
		img_original.id = "original_"+name;
		img_original.classList.add('original');
        	img_original.src=URL.createObjectURL(file);
		div_original.appendChild(img_original);

		i++;
		
		console.log(file)
	}

}

let contexts = {}
function initializeCells(files){

	var source = document.getElementById('blueprint')
 	var div_results = document.getElementById('all_results')
	div_results.innerHTML = ""
	newW = Math.min(winW/2,600)
	newW = 200

	contexts = {}

	for(const i in files){

		var name = files[i].name
		let new_element = source.cloneNode(true)
		new_element.id = "block_"+name

		var canvas = new_element.getElementsByTagName("canvas")
    		var ctx = canvas[0].getContext('2d');

		contexts[name] = ctx;

		div_results.appendChild(new_element)
	}
}

async function predict_all(files){
     	await postPictures(files, "predict_damages", saveJson)
     	await postPictures(files, "predict_plates", saveJson)
	showResult(files, save_json)
}

function postPictures(files, action, callback) {

	let formData = new FormData();
	for (const file of files) {
    		formData.append('file', file, file.name);
  	}

	var myInit = {
		method: 'POST',
		headers: new Headers(),
	    	// cache: 'default',
	    	// mode: 'cors',
	    	body: formData
    	}

    	return fetchRetry( api_url+action, myInit )
    	.then( response => response.json() )
    	.then( json => callback(json, files, action) )
    	.catch( error => console.error('error:', error) );
}

let save_json = []
function saveJson(json, files, action){
	console.log("saveJson:"+action+" / "+(files.length-1))

	switch(action){
		case "predict_damages":

			new_item = {
				'damages_json':json,
				'plates_json': null,
			}
			save_json = new_item;
			break;

		case "predict_plates":
			save_json['plates_json'] = json
			break;
	}
}


function showResult( files, jsons ){
	
	for(const file of files){
 		var div_source = document.getElementById("block_"+file.name);

		var loader_div = div_source.getElementsByClassName("loader");
		loader_div[0].style.display = 'none';

		var canvas_div = div_source.getElementsByClassName("canvas");
		canvas_div[0].style.display = 'block';

		var canvas = div_source.getElementsByTagName("canvas")
		newW = Math.min(winW/2,600)
		drawContextBackground(canvas[0], file.name, newW, newW);
	}

	for(const file of files){
		let i = 0
		for(const plate of jsons['plates_json']['plates']){
			if(plate.file == file.name)
			{
 				var div_source = document.getElementById("block_"+file.name);
				var result_cell = div_source.getElementsByClassName('result')

				addBulletPlates(result_cell[0], plate, i)
				drawContextPlate(file.name, plate, i);

				i++;
			}
		}

		i = 0
		for(const damage of jsons['damages_json']['damages']){
			if(damage.file == file.name)
			{
 				var div_source = document.getElementById("block_"+file.name);
				var result_cell = div_source.getElementsByClassName('result')

				addBulletDamages(result_cell[0], damage, i, damage.probable_duplicate)
				drawContextDamage(file.name, damage, i);

				i++;
			}
		}
	}
	var jsons_cell = document.getElementById('json_result')
	jsons_cell.innerHTML = "<br><strong>Damages</strong><br>"+JSON.stringify(jsons['damages_json'])
	jsons_cell.innerHTML += "<br><br><strong>Plates</strong><br>"+JSON.stringify(jsons['plates_json'])
}

function addBulletDamages(result_cell, damage, index, is_duplicate){

	var duplicate_text = (is_duplicate) ? " (probable duplicate)" : "";
	var duplicate_class = (is_duplicate) ? " class='duplicate'" : "";

	result = "<h3 "+duplicate_class+">Damage "+index+duplicate_text+"</h3><ul "+duplicate_class+">"
	for (const [key, value] of Object.entries(damage)) {
		if( ['action', 'severity', 'type', 'price', 'file'].includes(key) ){
			result += "<li><strong>"+key+":</strong> "+value+"</li>";
		}
	}

	result += "</ul>"
	result_cell.innerHTML += result
}

function addBulletPlates(result_cell, plate, index){

	result = "<h3>Plate "+index+"</h3><ul>"
	for (const [key, value] of Object.entries(plate)) {
		if( ['text'].includes(key) ){
			result += "<li><strong>"+key+":</strong> "+value+"</li>";
		}
	}
	result += "</ul>"
	result_cell.innerHTML += result
}

// --- DRAW DAMAGES & PLATES

colors = [
	'#FF0000', // RED
	'#0000FF', // BLUE
	'#FF00FF', // MAGANTA
	'#FFC000', // ORANGE
	'#00CC00', // GREEN
	'#FFFC00', // YELLOW
	'#00FFFF', // CYAN
]


function drawContextBackground(canvas, name, newWidth, newHeight)
{
 	let image = document.getElementById('original_'+name);
	let ctx = contexts[name];

	canvas.width = newWidth;
        canvas.height = newHeight;

	ctx.ratioW = newWidth/image.width;
	ctx.ratioH = newHeight/image.height;
	ctx.j = 0;

        ctx.drawImage(image, 0, 0, newWidth, newHeight);
}

function drawContextDamage(name, damage, i){

	let ctx = contexts[name];

 	x = (damage.coords[0])*ctx.ratioW;
 	y = (damage.coords[1])*ctx.ratioH;
 	w = (damage.coords[2]-damage.coords[0])*ctx.ratioW;
 	h = (damage.coords[3]-damage.coords[1])*ctx.ratioH;
 
 	if(damage.probable_duplicate == true){
 		ctx.setLineDash([3, 3]);
 		ctx.globalAlpha = 0.75;
 		color = "black";
 	} else {
 		ctx.setLineDash([]);
 		ctx.globalAlpha = 1.0;
 		color = colors[ctx.j % colors.length];
 		ctx.j++;
 	}
 
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
}

function drawContextPlate(name, plate, i){

	let ctx = contexts[name];
	
 	x = (plate.coords[0])*ctx.ratioW;
 	y = (plate.coords[1])*ctx.ratioH;
 	w = (plate.coords[2]-plate.coords[0])*ctx.ratioW;
 	h = (plate.coords[3]-plate.coords[1])*ctx.ratioH;

	ctx.lineWidth = 3;
	ctx.setLineDash([10, 5]);

	ctx.beginPath();
	ctx.rect(x, y, w, h)
	ctx.strokeStyle = "#FF0000";
	ctx.stroke();
	ctx.lineWidth = 1;
}
