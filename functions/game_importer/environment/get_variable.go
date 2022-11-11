package environment

import (
	"log"
	"os"
)

func GetVariable(key string) string {
	value := os.Getenv(key)

	if value == "" {
		log.Fatalf("Error loading required environment variable: %s", key)
	}

	return value
}
