[![Main Branch: API](https://github.com/mdryden/110yards/actions/workflows/main_api.yml/badge.svg)](https://github.com/mdryden/110yards/actions/workflows/main_api.yml) [![Main Branch: Web](https://github.com/mdryden/110yards/actions/workflows/main_web.yml/badge.svg)](https://github.com/mdryden/110yards/actions/workflows/main_web.yml) [![Main Branch: Rules](https://github.com/mdryden/110yards/actions/workflows/main_rules.yml/badge.svg)](https://github.com/mdryden/110yards/actions/workflows/main_rules.yml)

<img src="https://img.shields.io/badge/gitmoji-%20%F0%9F%8F%88%20%F0%9F%8D%81-FFDD67.svg" alt="gitmoji" />

# 110yards

As of November, 2021, 110 Yards is an open source project.

Please be aware up front that this project was not initially open, and the documentation of the dev procedure is new. As such, there may be errors or omissions in this documentation; please don't hesitate to contact me (the Discussions feature on GitHub is a good option) for help. Pull requests are welcome if you can help improve the docs.

## How to contribute

If you have made changes you think should be introduced into the project, please create a pull request. Please run all unit tests and apply the project formatting rules before creating the PR.

Unit and/or UI tests for your PR are greatly encouraged.

## Development Environment

### Pre-requisites

Note: Environment configuration instructions are intended for a Linux-based workflow. WSL2 is recommended if developing on Windows. Instructions should also work on MacOS, but have not been tested.

The following dependencies should be installed for development:

1. Python 3.10 (a virtual environment is recommended):

```
$ python3.10 -m venv .venv
```

2. Node 16

3. Firebase SDK:

```
$ npm install -g firebase-tools
```

4. Java 1.8+ (https://openjdk.java.net/install/)

```
$ sudo apt-get install openjdk-8-jre
```

After configuring pre-requisite tools and activating the virtual environment (if desired), you can install dependencies with the following command:

```
$ npm run config:dependencies
```

For Windows, use the following command:

```
$ npm run config:dependencies:win
```

### Configuring the dev environment

All projects are configured using environment variables. These environment variables can be set without actually changing your computer's environment variables by using
"dot env" files. You will need to create a file named ".env" in both the ./api and ./web folders in order to run those applications.

#### Sample API .env

```
DEV=True
CURRENT_SEASON=2022 # TODO: this should be a firestore switch
SEASON_WEEKS=21 # TODO: this should be a firestore switch

API_KEY=000000
FIREBASE_API_KEY=000000
GCLOUD_PROJECT=yards-dev

ORIGINS=http://localhost:8080
ENDPOINT=http://localhost:8000

FIRESTORE_EMULATOR_HOST="localhost:9000"
FIREBASE_AUTH_EMULATOR_HOST="localhost:9099"
PUBSUB_EMULATOR_HOST="localhost:9085"
RTDB_EMULATOR_HOST="localhost:9001"
```

#### Sample Web Client .env

```
VUE_APP_FIRESTORE_EMULATOR_PORT=9000
VUE_APP_AUTH_EMULATOR_HOST="http://localhost:9099"

VUE_APP_FIREBASE_API_KEY=000000
VUE_APP_FIREBASE_PROJECT=yards-dev
VUE_APP_WEB_URL=http://localhost:8080
VUE_APP_API_110_YARDS_URL=http://localhost:8000
VUE_APP_SITE_OFFLINE_MESSAGE=
```

### Running in local development mode

There are 3 components that must be started when running locally:

- Firebase Emulators
- Python API
- Vue Web App

You can start all of these with a single command from the root of the workspace:

```
$ npm run start
```

This command starts all 3 components using an NPM tool called [run-pty](https://github.com/lydell/run-pty/).

The icon beside each component indicates status:

⚪ = Loading/reloading
🟢 = Up
🟡 = Warning detected
🔴 = Error detected

Follow the run-pty prompts to view console output for a specific component.

You can also start them individually:

```
$ npm run start:api # start the Python API
$ npm run start:web # start the Vue Web App
$ npm run start:emulators # start the Firebase Emulators
```

**Note: after starting the emulators for the first time, you should run the following commands to configure switches:**

```
$ gcloud auth application-default login # configures default credentials for the emulator
$ npm config:switches # runs scripts to create required data in firestore
```

### Authentication

Assuming you have run the dev setup, there will be a user configured with the email address "admin@110yards.dev" (it's not a real account, don't bother trying in test or live!). This user account has admin access and can be used for general testing, or for testing admin functions.

Passwordless login requests do not send login links via email when using the emulator. To retrieve the login link for an email sign in in dev, open up the Firebase Emulator UI, navigate to logs, and look for the log message there. Copy and paste the full link to complete your sign in.

TODO: implement support for Google Login in the emulator. The emulator supports this, but in test/live a cloud function handles creating the profile in Firestore after the user registers. This workflow does not currently work in dev, so all testing should be done using email sign in.

### Invoking the API

Endpoints intended to be hit by clients require a firebase auth bearer token.

Endpoints intended to be hit by pub/sub pushes require the api key to be supplied in the Authorization header

You can create a bearer token to use with a REST client by supplying credentials to the following API endpoint:

http://localhost:8000/login

The payload for this request should be JSON in the following format:

```
{
    "email": "admin@110yards.dev",
    "password": "<user_password>"
}
```

**Note:** You will need to assign a password to the admin account (in the Firebase Auth Emulator) before you can use this endpoint. Firebase Emulator UI > Authentication > Admin (3 dots to the right) > Edit. You can also create a new account in the emulator just for invoking the API.

### Troubleshooting

**Black screen in the web client**

Did you run `npm run config:switches` while the emulator was running? Chances are that the switches have not been initialized, and the website is waiting to get them before completing startup.

You can confirm this is the issue if you have Vue DevTools installed; if you view data under the Root component, "switches" should be an Object. If it's null, it's because there are no configured switches in your firestore emulator instance.

**Can't launch the emulators (port not available)**

If this is because the emulators didn't shut down previously, you can find the process ids for the emulator(s) with the following command:

```
$ lsof -i :<port> # eg: lsof -i :9099 would find the auth emulator
$ kill -9 <pid of found process>
```

Repeat until you've found and killed all of the emulator processses.

### Creating and restoring a production firebase backup

Create the target data folder on your local machine:

```
$ mkdir .data.test
```

Export firestore to a cloud storage bucket:

```
$ gcloud firestore export gs://<project_id>.appspot.com/test_backup
```

Download backup:

```
$ gsutil -m cp -r gs://<project_id>.appspot.com/test_backup ./.data.test
```

Copy the firebase-export-metadata.json file from the .data folder which exists if you have run the emulator once before. Edit the copy so that the metadata_file attribute points at the exported data (test_backup/test_backup.overall_export_metadata, if using the names from this guide).

Export authentication data:

```
$ firebase auth:export accounts.json --format=json
```

Import authentication data by copying accounts.json to ./.data.test/auth_export

If using the names in this guide, you will need to manually start the emulators with this command in order to work with this data:

```
$ firebase emulators:start --only firestore,auth --import=./.data.test --export-on-exit --project yards-dev
```

## Deploying to production environments

### Test

All commits to the "test" branch will be automatically deployed to the test environment.

To deploy a pull request to test, reset the test branch to the PR branch:

```
$ git checkout test # switch to test branch
$ git reset --hard origin/<branch_name> # reset test branch to pr branch
$ git push --force # replace the origin test branch with your local copy
```

### Live

All commits to the "main" branch will be automatically deployed to the live environment.

### Other environments / development projects

If you have configured a project in GCP to host the API, you can deploy to that using the scripts that CI uses:

#### API

```
$ cd api
$ ./archive.sh <tag> <project>
$ ./deploy.sh <tag> <project> <project> <endpoint> <origins>
```

Options:
TAG = any valid docker image tag (eg: dev)
PROJECT = your google project id (note: this is intentionally included twice during deployment)
ENDPOINT = the expected cloud run URL after deploying (if you've never used cloud run on this project before, use a dummy value and then re-deploy after you know it)
ORIGINS = CORS origins for the deployed API. Can be "\*" for testing purposes.
