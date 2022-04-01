# TELEGRAM BOT

Spec document for the Bot
## STAKEHOLDERS

- Patients
- Nurses
- Dashboard
- Clinic Administrator

## ACTORS

- Dashboard (provides information to return to the user on request)
- Nurses (the only people authorized)

## FUNCT REQS

| N. req  | Description |
| ------- | ----------- |
| 1       | Extract information from the Dashboard |
|         | Update information on the Dashboard
|         | (What kind?)|
| 2       | Manage alerts |
| 2.1     | Receive alerts |
| 2.2     | Send warning messages to the medical staff |
| 3       | Manage patients |
| 3.1     | Register patients |
| 3.2     | Remove patients |
| 3.3     | Edit patients |
| 4       | Set rooms |
| 4.1     | Set desired Room Temperature |
| 4.2     | Set desired Room Lighting |

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

## USE CASES

## USE CASE DIAGRAM

## DEPLOYMENT DIAGRAM

## SYSTEM DIAGRAM

- Cloud: Where the Bot resides
- Mobile phones and PCs: Where the Users can access the Bot
