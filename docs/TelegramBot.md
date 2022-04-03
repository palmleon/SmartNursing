# TELEGRAM BOT

Specification document for the Bot.

## STAKEHOLDERS

- Patients
- Nurses
- Dashboard
- System Administrator

## ACTORS

- Dashboard (provides information to return to the user on request)
- Nurses (the only people authorized)
- System Administrator

## INTERFACE (!)

## FUNCT REQS

| N. req  | Description |
| ------- | ----------- |
| 1       | Interact with the Dashboard |
| 1.1     | Extract information from the Dashboard |
| 2       | Manage alerts |
| 2.1     | Receive alerts |
| 2.2     | Send warning messages to the medical staff |
| 3       | Manage patients |
| 3.1     | Register patients |
| 3.2     | Remove patients |
| 3.3     | Edit patients |
| 4       | Manage rooms |
| 4.1     | Set desired Room Temperature |
| 4.2     | Set desired Room Lighting |
| 4.3     | Monitor Room Temperature |
| 4.4     | Monitor Room Lighting |

## NON-FUNC REQS

| Type of req | Description |
| ----------- | ----------- |
| Usability   | Command names must be clear wrt their purpose |
| Usability   | Staff should be able to understand the commands and their usage in 5 minutes |
| Performance | Alerts should be forwarded to the user in < 5 sec |
| Performance | Data from dashboard should be displayed in < 5 sec |
| Extendability | The bot may include further features and should be able to integrate them easily without changing the overall structure of the bot |
| Availability | The bot should be available 99% of the time |
| Scalability | Every metric of the bot should not depend on the n. users involved |
| Security    | Authenticate User (Nurse, System Admin) |

## USE CASE SCENARIO

### Scenario 1: Authenticate User

| Field | Description |
| ------| ----------- |
| Actor | Nurse |
| Pre-condition | User is not authenticated |
| Post-condition | User is authenticated |
| Steps | User is asked to insert its ID and password |
| | The system checks whether the user exists and the password is correct |
| | The system informs the user that he/she has been authenticated |

### Scenario 2: User looks for info about a patient

| Field | Description |
| ------| ----------- |
| Actor | Nurse, System Administrator |
| Pre-condition | User looks for a specific information about a patient |
|               | User is authenticated |
| Post-condition | User retrieves the information |
| Steps | User launches a command for searching information about patients |
|       | User prompts the Patient ID and the kind of information required |
|       | The system checks whether the Patient exists and that kind of information is available |
|       | The system returns the desired information |

### Scenario 3: System Administrator registers a patient

| Field | Description |
| ------| ----------- |
| Actor | System Administrator |
| Pre-condition | A patient of the clinic is not present in the catalog |
|               | User is authenticated |
| Post-condition | The patient is successfully inserted into the catalog |
| Steps | The User launches a command for inserting new patients |
|       | The User inputs the Patient Data and all kind of information that are available at registration time (Patient ID can be defined manually or not)|
|       | The system verifies that the Patient Data are not already present (i.e. there is no other Patient with exactly the same data) |
|       | The system registers the patient and returns a success message to the User |

### Scenario 3.1: Nurse registers a patient

| Field | Description |
| ------| ----------- |
| Actor | Nurse |
| Pre-condition | A patient of the clinic is not present in the catalog |
|               | User is authenticated |
| Post-condition | The patient is successfully inserted into the catalog |
| Steps | The User launches a command for inserting new patients |
|       | The User inputs the Patient Data and all kind of information that are available at registration time (Patient ID can be defined manually or not)|
|       | The system verifies that the Patient Data are not already present (i.e. there is no other Patient with exactly the same data) |
|       | The system forwards the request to a System Administrator, who is the only role authorized to perform this kind of operation |
|       | System Administrator registers a patient: See Scenario 3.2 |

### Scenario 3.2: System Administrator handles a Patient Registration Request

| Field | Description |
| ------| ----------- |
| Actor | System Administrator |
| Pre-condition | A patient of the clinic is not present in the catalog |
|               | User is authenticated |
|               | A Registration Request has been forwarded to the User |
| Post-condition | The patient is successfully inserted into the catalog |
| Steps | The User reads a notification of a Registration Request |
|       | The User can read and analyze the Request and all data submitted |
|       | The User decides whether to accept the Request |
|       | The system follows the User decision and returns an acknowledge message |

### Scenario 4: System Administrator removes a patient

| Field | Description |
| ------| ----------- |
| Actor | System Administrator |
| Pre-condition | A patient of the clinic must be removed and is present in the catalog |
|               | User is authenticated |
| Post-condition | The patient is no longer present in the catalog |
| Steps | The User launches a command for removing a patient |
|       | The User inputs either the Patient ID or their name |
|       | If the Patient ID is input: |
|       | - The system verifies that the Patient ID exists |
|       | - The system removes the patient |
|       | - The system returns a success message to the User |
|       | If the Patient Name is input: |
|       | - The system looks for all Patients with that name |
|       | - The system shows to the user all Patients with that name and their data and asks to choose which one to remove|
|       | - The user chooses the user to remove |
|       | - The system returns a success message to the User |

### Scenario 4.1: Nurse removes a patient

| Field | Description |
| ------| ----------- |
| Actor | Nurse |
| Pre-condition |  A patient of the clinic must be removed and is present in the catalog |
|               | Input from the User is valid (Patient ID/Name exists) |
|               | User is authenticated |
| Post-condition | The patient is no longer present in the catalog |
| Steps | The User launches a command for removing a patient |
|       | The User inputs either the Patient ID or their name |
|       | If the Patient ID is input: |
|       | - The system verifies that the Patient ID exists |
|       | - The system forwards the request to a System Administrator |
|       | - The system informs that a System Administrator will handle the request |
|       | - The System Administrator handles the request: see Scenario 4.2 |
|       | If the Patient Name is input: |
|       | - The system looks for all Patients with that name |
|       | - The system shows to the user all Patients with that name and their data and asks to choose which one to remove|
|       | - The user chooses the user to remove |
|       | - The system informs that a System Administrator will handle the request |
|       | - The System Administrator handles the request: see Scenario 4.2 |

### Scenario 4.2: System Administrator handles a Patient Removal Request

| Field | Description |
| ------| ----------- |
| Actor | System Administrator |
| Pre-condition | A patient of the clinic is present in the catalog and must be removed|
|               | User is authenticated |
|               | A Removal Request has been forwarded to the User |
| Post-condition | The patient is successfully inserted into the catalog |
| Steps | The User reads a notification of a Removal Request |
|       | The User can read and analyze the Request and all data submitted |
|       | The User decides whether to accept the Request |
|       | The system follows the User decision and returns an acknowledge message |

### Scenario 5: System Administrator edits a patient

| Field | Description |
| ------| ----------- |
| Actor | System Administrator|
| Pre-condition | A patient of the clinic is present in the catalog and must be edited |
|               | Input from the User is valid |
|               | User is authenticated |
| Post-condition | Patient Data is successfully edited |
| Steps | The User launches a command for editing patients |
|       | The User inputs either the Patient ID or their name |
|       | If the Patient ID is input: |
|       | - The system verifies that the Patient ID exists |
|       | - The system asks which field(s) should be edited for the patient |
|       | - The User edits them |
|       | - The system updates its information |
|       | - The system returns a success message to the User |
|       | If the Patient Name is input: |
|       | - The system looks for all Patients with that name |
|       | - The system shows to the user all Patients with that name and their data and asks to choose which one to edit |
|       | - The system asks which field(s) should be edited for the patient |
|       | - The User edits them |
|       | - The system updates its information |
|       | - The system returns a success message to the User |

### Scenario 5.1: Nurse edits a patient

| Field | Description |
| ------| ----------- |
| Actor | Nurse |
| Pre-condition | A patient of the clinic is present in the catalog and must be edited |
|               | Input from the User is valid |
|               | User is authenticated |
| Post-condition | Patient Data is successfully edited |
| Steps | The User launches a command for editing a patient |
|       | The User inputs either the Patient ID or their name |
|       | If the Patient ID is input: |
|       | - The system verifies that the Patient ID exists |
|       | - The system asks which field(s) should be edited for the patient |
|       | - The User edits them |
|       | - The system forwards the request to a System Administrator |
|       | - The system informs that a System Administrator will handle the request |
|       | - The System Administrator handles the request: see Scenario 5.2 |
|       | If the Patient Name is input: |
|       | - The system looks for all Patients with that name |
|       | - The system shows to the user all Patients with that name and their data and asks to choose which one to edit|
|       | - The user chooses the user to edit |
|       | - The system asks which field(s) should be edited for the patient |
|       | - The User edits them |
|       | - The system informs that a System Administrator will handle the request |
|       | - The System Administrator handles the request: see Scenario 5.2 |

### Scenario 5.2: System Administrator handles a Patient Edit Request

| Field | Description |
| ------| ----------- |
| Actor | System Administrator |
| Pre-condition | A patient of the clinic is present in the catalog and must be edited|
|               | User is authenticated |
|               | An Edit Request has been forwarded to the User |
| Post-condition | Patient Data is successfully edited |
| Steps | The User reads a notification of an Edit Request |
|       | The User can read and analyze the Request and all data submitted |
|       | The User decides whether to accept the Request |
|       | The system follows the User decision and returns an acknowledge message |

### Scenario 6: Warning the staff that there is a medical emergency

| Field | Description |
| ------| ----------- |
| Actor | Nurses |
| Pre-condition | A patient in the clinic has a medical emergency |
|               | The patient is already present in the catalog |
|               | Users are authenticated and always logged in |
| Post-condition | Users are informed of the emergency and can handle it |
| Steps | The system receives a warning from monitoring modules |
|       | The system reads the list of all Users that are currently working in the clinic |
|       | The system forwards the warning to those Users |

### Scenario 7: User sets desired Room Temperature/Lighting

| Field | Description |
| ------| ----------- |
| Actor | Nurses |
| Pre-condition | The Room exists and is registered |
|               | User is authenticated |
| Post-condition | Room Temperature/Lighting is set |
| Steps | The User launches a command to set the Room parameters |
|       | The User selects the Room to set |
|       | The system verifies whether the Room is registered |
|       | The User selects the parameter to modify |
|       | The User sets the new value for the parameter |
|       | The system forwards the request to the Room Temperature/Lighting manager |

### Scenario 8: User monitors Room Temperature/Lighting

| Field | Description |
| ------| ----------- |
| Actor | Nurses |
| Pre-condition | The Room exists and is registered |
|               | User is authenticated |
| Post-condition | Room Temperature/Lighting value can be read |
| Steps | The User launches a command to read the current Room parameters |
|       | The User selects the Room to set |
|       | The system verifies whether the Room is registered |
|       | The User selects the parameter to read |
|       | The system forwards the request to the Room Temperature/Lighting manager, asking for the searched value |
|       | The User reads the value for the parameter |

### Scenario 9: System Administrator registers a new Room

| Field | Description |
| ------| ----------- |
| Actor | System Administrator |
| Pre-condition | The Room exists but is not present in the catalog yet |
|               | User is authenticated |
| Post-condition | The Room is registered correctly in the catalog |
| Steps | The User launches a command to register a new Room |
|       | The User defines the ID of the new Room (manually or automatically)|
|       | The system verifies whether a Room with the same ID already exists (in case of manual definition of the Room ID) |
|       | The system forwards the request to the Room and Patient catalog, which proceeds to fulfill it |

Exception Scenarios:

- User is not authenticated successfully
- User looks for a patient/room, but it does not exist
- User tries to register a duplicate patient
- User tries to register a patient with invalid input
- User tries to remove a patient that does not exist
- User tries to edit a patient that does not exist
- Invalid input
- The Bot tries to warn the staff, but the message is lost
- User tries to manage a Room that does not exist
- System Administrator tries to register a duplicate Room

### Scenario 3: User registers a patient

| Field | Description |
| ------| ----------- |
| Actor |  |
| Pre-condition |  |
| Post-condition |  |
| Steps |  |

### Scenario 3: User registers a patient

| Field | Description |
| ------| ----------- |
| Actor |  |
| Pre-condition |  |
| Post-condition |  |
| Steps |  |

### Scenario 3: User registers a patient

| Field | Description |
| ------| ----------- |
| Actor |  |
| Pre-condition |  |
| Post-condition |  |
| Steps |  |

### Scenario 3: User registers a patient

| Field | Description |
| ------| ----------- |
| Actor |  |
| Pre-condition |  |
| Post-condition |  |
| Steps |  |

### Scenario 3: User registers a patient

| Field | Description |
| ------| ----------- |
| Actor |  |
| Pre-condition |  |
| Post-condition |  |
| Steps |  |

### Scenario 3: User registers a patient

| Field | Description |
| ------| ----------- |
| Actor |  |
| Pre-condition |  |
| Post-condition |  |
| Steps |  |

### Scenario 3: User registers a patient

| Field | Description |
| ------| ----------- |
| Actor |  |
| Pre-condition |  |
| Post-condition |  |
| Steps |  |

### Scenario 3: User registers a patient

| Field | Description |
| ------| ----------- |
| Actor |  |
| Pre-condition |  |
| Post-condition |  |
| Steps |  |

### Scenario 3: User registers a patient

| Field | Description |
| ------| ----------- |
| Actor |  |
| Pre-condition |  |
| Post-condition |  |
| Steps |  |

### Scenario X

| Field | Description |
| ------| ----------- |
| Actor |  |
| Pre-condition |  |
| Post-condition |  |
| Steps |  |

## USE CASE DIAGRAM

## DEPLOYMENT DIAGRAM

- On Mobile Phones (users): Telegram
- On the Raspberry: the Telegram Bot (which must communicate with the rest of the system via MQTT) (?) - see below

## SYSTEM DIAGRAM

- Raspberry: Where the Bot resides (?) - The bot is unique, and we could have more than one Raspberry. So, where should it reside?
- Mobile phones and PCs: Where the Users can access the Bot
