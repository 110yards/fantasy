package tests

import (
	"log"
	"testing"
	"time"

	"github.com/joho/godotenv"
	"github.com/mdryden/110yards/functions/gameimporter/environment"
	"github.com/mdryden/110yards/functions/gameimporter/importer"
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

	games, err := importer.GetGamesForSeason(environment.CflKey, year)

	assert.NoError(t, err)
	assert.NotNil(t, games)
	assert.Equal(t, gameCount, len(games))
}

func TestParseIsoString(t *testing.T) {
	expected := time.Date(2022, time.June, 9, 21, 0, 0, 0, time.FixedZone("", -4*3600))
	actual, err := importer.ParseIsoString("2022-06-09T21:00:00-04:00")

	assert.NoError(t, err)
	assert.Equal(t, expected, actual)
}

func TestFilterRecentGames(t *testing.T) {

	const daysBack = 2
	const daysForward = 1

	currentDate := time.Date(2022, time.June, 9, 21, 0, 0, 0, time.FixedZone("", -4*3600))

	lastWeek := importer.JsonObject{"date_start": "2022-06-02T21:00:00-04:00"}
	yesterday := importer.JsonObject{"date_start": "2022-06-08T21:00:00-04:00"}
	today := importer.JsonObject{"date_start": "2022-06-09T21:00:00-04:00"}
	nextWeek := importer.JsonObject{"date_start": "2022-06-16T21:00:00-04:00"}

	games := []importer.JsonObject{
		lastWeek,
		yesterday,
		today,
		nextWeek,
	}

	recent, err := importer.FilterRecentGames(games, currentDate, daysBack, daysForward)

	assert.NoError(t, err)
	assert.Equal(t, 2, len(recent))
}

func TestGetFullGame(t *testing.T) {
	setupEnvironment()

	const year = 2022
	const gameId = 6211

	game, err := importer.GetFullGame(environment.CflKey, year, gameId)

	assert.NoError(t, err)
	assert.NotNil(t, game)

	assert.NotNil(t, game["boxscore"])
	assert.NotNil(t, game["play_by_play"])
	assert.NotNil(t, game["rosters"])
}

func TestHashChangesForDifferentObjects(t *testing.T) {
	game1 := importer.JsonObject{"foo": "bar", "value": true}
	game2 := importer.JsonObject{"foo": "bar", "value": false}

	hash1, err1 := importer.CalculateHash(game1)
	hash2, err2 := importer.CalculateHash(game2)

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
