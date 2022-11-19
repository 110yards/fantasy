package environment

import (
	"log"

	"github.com/joho/godotenv"
)

var CflKey string
var RtdbEmulatorHost string
var ProjectId string
var IsDev bool

func Setup() {

	if err := godotenv.Load(".env"); err != nil {
		log.Print(".env file NOT loaded")
	} else {
		log.Print(".env added to environment")
	}

	log.Print("Loaded environment")
	CflKey = getRequired("CFL_API_KEY")
	ProjectId = getRequired("GCLOUD_PROJECT")
	RtdbEmulatorHost = getOptional("RTDB_EMULATOR_HOST", "")
	IsDev = getOptionalBool("IS_DEV", false)
}
