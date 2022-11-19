package scheduler

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
)

const cflApi = "https://api.cfl.ca"
const eventTypeRegularSeason = 1

func v1Url(key, path string) string {
	if strings.Contains(path, "?") {
		path += fmt.Sprintf("&key=%s", key)
	} else {
		path += fmt.Sprintf("?key=%s", key)
	}

	return fmt.Sprintf("%s/v1/%s", cflApi, path)
}

func GetGamesForSeason(key string, year int) (*GamesResponse, error) {
	path := fmt.Sprintf("games/%d?page[size]=100", year)
	url := v1Url(key, path)

	resp, err := http.Get(url)

	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("request to %s returned status code %d", path, resp.StatusCode)
	}

	responseBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var result GamesResponse
	err = json.Unmarshal(responseBody, &result)

	return &result, err
}
