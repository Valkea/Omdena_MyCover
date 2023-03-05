# API for the MyCover Omdena's project

You will find in the section below, all the instructions required to run the API on your own computer.
 
1 - in the first section, I will describe how to run it from the source (so you can modify the API)<br>
2 - in the second section, I will explain how to use the API from the docker I prepared and deployed on the Docker Hub.

## 1. Run the API locally from sources
(You will need Omdena's credential for this part, but if you don't have these credentials, you can try out the Docker version at the bottom)

### First, 
let's duplicate the project github repository

```bash
>>> git clone https://dagshub.com/Omdena/MyCover.git
>>> cd MyCover/task_5_model_deployment/API_Emmanuel_Letremble/
```

### Secondly,
let's clone the large file with DVC *(you need to install [DVC](https://dvc.org) prior to using the following command line)*:
```bash
>>> dvc remote add origin https://dagshub.com/Omdena/MyCover.dvc
>>> dvc remote modify origin --local auth basic 
>>> dvc remote modify origin --local user YOUR_LOGIN
>>> dvc remote modify origin --local password YOUR_PASSWORD
>>> dvc pull -r origin
```

### Thirdly,
let's create a virtual environment and install the required Python libraries

(Linux or Mac)
```bash
>>> python3 -m venv venvMyCover
>>> source venvMyCover/bin/activate
>>> pip install -r requirements.txt
```

(Windows):
```bash
>>> py -m venv venvmycover
>>> .\venvmycover\Scripts\activate
>>> py -m pip install -r requirements.txt
```

### Running API server locally using python scripts

Start both API and CLIENT Flask servers:
```bash
(venv) >> python API_client_server.py
```
Stop with CTRL+C *(once the tests are done, from another terminal...)*


### Tests

> One can check that the server is running by opening the following url:<br>
> http://0.0.0.0:5000/

> Then you can `post` an image to: <br>
> * http://0.0.0.0:5000/predict_damages <br>
> and it will return a json encoded array of the predicted damages.<br>
> 
> * http://0.0.0.0:5000/predict_plate <br>
> and it will return a json encoded array of the predicted plate text.<br>
>
> Postman instructions:
> 1. create a POST query with one of the two previous URL,
> 2. add a field named 'file' of type File in Body/form-data),
> 3. select an image to send with the request,
> 4. send the request and get the result.

> You can also use the simple front-end available here:<br>
> * http://0.0.0.0:5000/upload_damages/ <br>
> * http://0.0.0.0:5000/upload_plate/ <br>
> When posting an image from this simple frontend, the data will be send to the /predict_damages or /predict_plate urls and the result will be displayed in HTML.

> Or even use the API Documentation `Try it out` button on the entrypoints.
> http://0.0.0.0:5000/docs

Note that the first request (particularly the plate request) might take some time. But once you've got the first prediction, it should run pretty fast for the others.

### Documentation

The API documentation is available at this endpoint: http://0.0.0.0:5000/docs



## 2. Docker

### Building a Docker image

```bash
>> docker build -t mycover .
```

### Running a local Docker image

```bash
>> docker run -it -p 5000:5000 mycover:latest
```

Then one can run the same test steps as before with curl, postman etc.

Stop with CTRL+C


### Pulling a Docker image from Docker-Hub

I pushed a copy of my docker image on the Docker-hub, so one can pull it:

```bash
>> docker pull valkea/mycover:latest
```

But this command is optionnal, as running it (see below) will pull it if required.

### Running a Docker image gathered from Docker-Hub

Then the command to start the docker is almost similar to the previous one:

```bash
>> docker run -it -p 5000:5000 valkea/mycover:latest
```

And once again, one can run the same curve or postman tests.

Stop with CTRL+C
