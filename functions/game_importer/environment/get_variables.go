package environment

import (
	"log"
	"os"
	"strconv"
)

func getRequired(key string) string {
	value := os.Getenv(key)

	if value == "" {
		log.Fatalf("Error loading required environment variable: %s", key)
	}

	return value
}

func getOptional(key string, defaultValue string) string {
	value := os.Getenv(key)

	if value == "" {
		value = defaultValue
	}

	return value
}

func getOptionalBool(key string, defaultValue bool) bool {
	value := os.Getenv(key)

	if value == "" {
		return defaultValue
	}

	v, err := strconv.ParseBool(value)
	if err != nil {
		log.Printf("Failed to parse value of %s (%s) as boolean, returning default (%v)", key, value, defaultValue)
		return defaultValue
	}

	return v
}
