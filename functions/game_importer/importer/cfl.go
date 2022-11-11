package importer

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
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

func getArray(key, path string) (JsonArray, error) {
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

	type cflResponse struct {
		Data   JsonArray                `json:"data"`
		Errors []map[string]interface{} `json:"errors"`
		Meta   map[string]interface{}   `json:"meta"`
	}

	var result cflResponse
	err = json.Unmarshal(responseBody, &result)

	return result.Data, err
}

func ParseIsoString(input string) (time.Time, error) {
	return time.Parse("2006-01-02T15:04:05-07:00", input)
}
