package tests

import (
	"log"
	"testing"

	"github.com/joho/godotenv"
	"github.com/mdryden/110yards/functions/gameimporter/importer"
	"github.com/mdryden/110yards/functions/schedulemanager/environment"
	"github.com/mdryden/110yards/functions/schedulemanager/scheduler"
	"github.com/stretchr/testify/assert"
)

func setupEnvironment() {
	err := godotenv.Load("../.env")

	if err != nil {
		log.Print("Error loading .env file (running in CI, maybe?)")
	}
	environment.Setup()
}

func TestGetGamesForSeason(t *testing.T) {
	setupEnvironment()

	const year = 2022
	const gameCount = 95

	schedule, err := scheduler.GetGamesForSeason(environment.CflKey, year)

	assert.NoError(t, err)
	assert.NotNil(t, schedule)
	assert.Equal(t, gameCount, len(schedule.Games))
}

func TestHashChangesForDifferentObjects(t *testing.T) {
	schedule1 := scheduler.Schedule{
		Games: map[int]scheduler.Game{
			1: {GameId: 1},
			2: {GameId: 2},
		},
	}
	schedule2 := scheduler.Schedule{
		Games: map[int]scheduler.Game{
			3: {GameId: 3},
			4: {GameId: 4},
		},
	}

	hash1, err1 := scheduler.CalculateHash(schedule1)
	hash2, err2 := scheduler.CalculateHash(schedule2)

	assert.NoError(t, err1)
	assert.NoError(t, err2)

	assert.NotEqual(t, hash1, hash2)
}

func TestHashDoesntChangeForMatchingObjects(t *testing.T) {

	game1 := importer.JsonObject{"foo": "bar", "value": true}
	game2 := importer.JsonObject{"foo": "bar", "value": true}

	hash1, err1 := importer.CalculateHash(game1)
	hash2, err2 := importer.CalculateHash(game2)

	assert.NoError(t, err1)
	assert.NoError(t, err2)

	assert.Equal(t, hash1, hash2)
}
