# API documentation
Save the address of the device and registry system in a local file called 'config.json'

## GET methods

*message broker*

`/message-broker`

RESPONSE json body, readable with request.json() method :
```
{
    port : 1234,
    name : test.mosquiotto.org
}
```

*telegram chat id list*

`/telegram-chat-id-list`

RESPONSE json body, readable with request.json() method :
```
[1,2,3,4]
```

*alarm base topic*

`/alarm-base-topic`

RESPONSE json body, readable with request.json() method :
```
group01/IoTProject/PatientAlarm/
```

*patients list*

`/patients`

RESPONSE json body, readable with request.json() method :
```
[{patint1}, {patient2}, ...]
```

*get single patient*

`/patient/:id`

RESPONSE json body, readable with request.json() method :
```
{
    patientID : 3
    others patient info
}
```

## POST methods

`/add-service`

REQUEST json body :
```
{
    serviceID : 7,
    name : xxx
}
```

You can file the id list of the services in the readme of the main branch

RETURN MESSAGES : 
- 400, if service already exists
- 201, operation ok


`/add-patient`

REQUEST json body :
```
{
    patientID : 7,
    other info
}
```
RETURN MESSAGES : 
- 400, if patient already exists
- 201, operation ok





## PUT methods


`/update-service`

REQUEST json body :
```
{
    serviceID : 7,
    name : xxx
}
```

You can file the id list of the services in the readme of the main branch

## DELETE methods


`/delete-patient/:id`

parameter : id of the patient to delete
RETURN MESSAGES : 
- 404, if patient not found
- 500, if id is not present in the url
- 200, operation ok



