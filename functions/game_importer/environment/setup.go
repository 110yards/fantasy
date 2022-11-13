package environment

import (
	"log"

	"github.com/joho/godotenv"
)

var CflKey string

func Setup() {

	if err := godotenv.Load(".env"); err != nil {
		log.Print(".env file NOT loaded")
	} else {
		log.Print(".env added to environment")
	}

	log.Print("Loaded environment")
	CflKey = GetVariable("CFL_API_KEY")
}
