# Project 6: Brevet Time Calculator Service

Calculates checkpoint opening and closing times using Flask and Ajax. Select the brevet distance and starting time, then enter checkpoint distances.

Submit saves the calculated controls to MongoDB. Display opens a separate page showing saved controls. Empty submissions, invalid distances, missing times, and database errors return error messages.

A REST API exports the saved control times in JSON or CSV. A PHP page in a separate container calls the API and displays the results.

## Rules

Supported brevet distances are 200, 300, 400, 600, and 1000 km. The calculator uses the ACP opening speeds and closing limits from Project 5. Displayed times are in UTC.

[Official ACP calculation rules](https://rusa.org/pages/acp-brevet-control-times-calculator)

## Run

```bash
cd DockerRestAPI
docker compose up --build
```

| Service | URL |
|---|---|
| Calculator | [http://localhost:5002](http://localhost:5002) |
| REST API | [http://localhost:5001/listAll](http://localhost:5001/listAll) |
| PHP consumer | [http://localhost:5003](http://localhost:5003) |


Calculate and submit a set of controls before checking the API and PHP page.

To stop the containers, run `docker compose down` from `DockerRestAPI`.

## API

| Endpoint | Returns |
|---|---|
| `/listAll` | Opening and closing times |
| `/listOpenOnly` | Opening times |
| `/listCloseOnly` | Closing times |

Each endpoint defaults to JSON. Add `/json` or `/csv` to choose the format. Use `?top=k` to return the earliest `k` times in ascending order.

- [First 3 opening times in CSV](http://localhost:5001/listOpenOnly/csv?top=3)
- [First 4 closing times in JSON](http://localhost:5001/listCloseOnly/json?top=4)

## Author

Sachit Srivastava (sachit@uoregon.edu)