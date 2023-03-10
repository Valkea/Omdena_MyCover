
// --- GLOBAL VARIABLES ---

const api_url = "http://ec2-54-74-190-189.eu-west-1.compute.amazonaws.com:5000/"

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
	document.getElementById(callback_id).innerHTML = myObj;
}

