package environment

import (
	"log"

	"github.com/joho/godotenv"
)

var RtdbEmulatorHost string
var ProjectId string

func Setup() {

	if err := godotenv.Load(".env"); err != nil {
		log.Print(".env file NOT loaded")
	} else {
		log.Print(".env added to environment")
	}

	log.Print("Loaded environment")
	ProjectId = getRequired("GCLOUD_PROJECT")
	RtdbEmulatorHost = getOptional("RTDB_EMULATOR_HOST", "")
}
