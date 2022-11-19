package scheduler

import (
	"context"
	"fmt"
	"log"

	"github.com/mdryden/110yards/functions/schedulemanager/store"
)

func UpdateSchedule(key string, year int) error {
	log.Printf("Importing %d schedule", year)

	resp, err := GetGamesForSeason(key, year)
	if err != nil {
		return fmt.Errorf("failed to fetch games for %d: %v", year, err)
	}

	if resp == nil {
		return fmt.Errorf("failed to fetch games for %d: response was nil", year)
	}

	log.Printf("Fetched %d data", year)

	previousHash, err := ReadScheduleHash(year)
	if err != nil {
		return err
	}

	schedule, err := CreateSchedule(year, resp.Games)

	if err != nil {
		return err
	}

	if schedule.Hash == previousHash {
		log.Printf("No changes to schedule detected")
		return nil
	}

	log.Printf("Schedule has changed, attempting to save...")

	return SaveSchedule(year, schedule)
}

func getSchedulePath(year int) string {
	return fmt.Sprintf("schedule/%d", year)
}

func ReadScheduleHash(year int) (string, error) {
	schedulePath := getSchedulePath(year)
	hashPath := fmt.Sprintf("%s/hash", schedulePath)

	var hash string
	err := store.ReadPath(context.Background(), hashPath, &hash)

	if err != nil {
		return "", err
	}

	return hash, nil
}

func SaveSchedule(year int, schedule Schedule) error {
	path := getSchedulePath(year)
	return store.SetPath(context.Background(), path, schedule)
}
