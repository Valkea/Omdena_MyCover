
// --- GLOBAL VARIABLES ---

const api_url = "http://ec2-54-74-190-189.eu-west-1.compute.amazonaws.com:5000/";
// const api_url = "http://127.0.0.1:5000/";
let ctx = undefined;

// --- FUNCTIONS

function postPicture(url, callback_id) {
   
	let formData = new FormData();
    	formData.append("file", fileupload.files[0]);

	var myInit = {
		method: 'POST',
		headers: new Headers(),
	    	// cache: 'default',
	    	// mode: 'cors',
	    	body: formData
    	}

    	return fetch( url, myInit )
    	.then( response => response.json() )
    	.then( json => callback(json, callback_id) )
    	.catch( error => console.error('error:', error) );
}

function predict_damages() {

	url = api_url + "predict_damages"
	callback_id = 'result_damages'

    	postPicture(url, callback_id)
}

function predict_plate() {

	url = api_url + "predict_plate"
	callback_id = 'result_plate'

    	postPicture(url, callback_id)
}

function callback(json, callback_id) {

	myObj = JSON.stringify(json);
	var image = document.getElementById('output');

	switch (callback_id){
		case "result_damages":

			var show_json = document.getElementById('show_damages_json');
			show_json.innerHTML = "<h2>JSON</h2>"+myObj;

			drawDamages(image, 200, 200, json.damages);

			var result_cell = document.getElementById('result_dmg')
			result_cell.innerHTML = "<h2>Damages</h2>"

			var i = 0
			for(let damage of json.damages){

				result = "<h3>"+i+"</h3><ul>"
				for (const [key, value] of Object.entries(damage)) {
					result += "<li><strong>"+key+":</strong> "+value+"</li>";
				}
				result += "</ul>"

				result_cell.innerHTML += result
				i++
			}

			break;
		
		case "result_plate":

			var show_json = document.getElementById('show_plate_json');
			show_json.innerHTML = "<h2>JSON</h2>"+myObj;

			drawPlate(image, 200, 200, json.plates);

			var result_cell = document.getElementById('result_plate')
			result_cell.innerHTML = "<h2>Plates</h2>"

			var i = 0
			for(let plate of json.plates){

				result = "<h3>"+i+"</h3><ul>"
				for (const [key, value] of Object.entries(plate)) {
					result += "<li><strong>"+key+":</strong> "+value+"</li>";
				}
				result += "</ul>"

				result_cell.innerHTML += result
				i++
			}

			break;

	}
}

function drawDamages(image, newWidth, newHeight, damages) {

    	//create an image object from the path
    	const originalImage = new Image();
    	originalImage.src = image.src;

    	const canvas = document.getElementById('canvas_damages');
    	ctx_dmg = canvas.getContext('2d');

        canvas.width = image.width;
        canvas.height = image.height;

        //draw the image
        ctx_dmg.drawImage(originalImage, 0, 0, image.width, image.height);

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
	for(let damage of damages){

		x = damage.coords[0]
		y = damage.coords[1]
		w = damage.coords[2]-damage.coords[0]
		h = damage.coords[3]-damage.coords[1]

		color = colors[i % colors.length]

		ctx_dmg.beginPath();
		ctx_dmg.rect(x, y, w, h)
		ctx_dmg.strokeStyle = color;
		ctx_dmg.stroke();

		ctx_dmg.globalAlpha = 0.1;
		ctx_dmg.fillStyle = "white";
		ctx_dmg.fillRect(x, y, w, h);
		ctx_dmg.globalAlpha = 1.0;

		ctx_dmg.font = "10px Arial";
		ctx_dmg.textAlign = "left";
		txt = i+" "+damage.type;
		let width = ctx_dmg.measureText(txt).width;

		ctx_dmg.fillStyle = "white";
		ctx_dmg.fillRect(x, y, width+10, 15);

		ctx_dmg.fillStyle = color;
		ctx_dmg.fillText(txt, x+5, y+10);
		i++;
	}
}

function drawPlate(image, newWidth, newHeight, plates) {

    	//create an image object from the path
    	const originalImage = new Image();
    	originalImage.src = image.src;

    	const canvas = document.getElementById('canvas_plate');
    	ctx_dmg = canvas.getContext('2d');

        canvas.width = image.width;
        canvas.height = image.height;

        //draw the image
        ctx_dmg.drawImage(originalImage, 0, 0, image.width, image.height);

	let i = 0
	for(let plate of plates){

		x = plate.coords[0]
		y = plate.coords[1]
		w = plate.coords[2]-plate.coords[0]
		h = plate.coords[3]-plate.coords[1]

		color = "#FF0000"

		ctx_dmg.beginPath();
		ctx_dmg.rect(x, y, w, h)
		ctx_dmg.strokeStyle = color;
		ctx_dmg.stroke();

		i++;
	}
}

function cropImage(imagePath, canvasTarget, newX, newY, newWidth, newHeight) {
    	console.debug("canvasTarget:"+canvasTarget);

    	//create an image object from the path
    	const originalImage = new Image();
    	originalImage.src = imagePath;

    	//initialize the canvas object
    	const canvas = document.getElementById(canvasTarget);
	if(ctx === undefined){
    		ctx = canvas.getContext('2d');
		console.log("on définit le ctx")
	};

        //set the canvas size to the new width and height
        canvas.width = newWidth;
        canvas.height = newHeight;

        //draw the image
        ctx.drawImage(originalImage, newX, newY, newWidth, newHeight, 0, 0, newWidth, newHeight);
}

function onLoadImage() {
	var image = document.getElementById('output');
        image.src=URL.createObjectURL(event.target.files[0]);
	// cropImage(image.src, 0, 0, 200, 200);
}
