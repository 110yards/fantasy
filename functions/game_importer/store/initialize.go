package store

import (
	"context"
	"fmt"
	"log"

	firebase "firebase.google.com/go/v4"
	"firebase.google.com/go/v4/db"
)

var RTDB *db.Client

func Initialize(rtdbEmulatorHost, projectId string) {
	ctx := context.Background()

	conf := &firebase.Config{
		DatabaseURL: getRealtimeDatabaseUrl(rtdbEmulatorHost, projectId),
	}

	app, err := firebase.NewApp(ctx, conf)

	if err != nil {
		log.Fatalf("Error initializing firebase: %v", err)
	}

	rtdb, err := app.Database(ctx)
	if err != nil {
		log.Fatalf("Error initializing rtdb: %v", err)
	}

	RTDB = rtdb
}

func getRealtimeDatabaseUrl(rtdbEmulatorHost, projectId string) string {
	if rtdbEmulatorHost != "" {
		return fmt.Sprintf("%s/?ns=%s", rtdbEmulatorHost, projectId)
	} else {
		return fmt.Sprintf("https://%s.firebaseio.com", projectId)
	}
}
