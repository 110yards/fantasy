package scheduler

import (
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
)

func CalculateHash(schedule Schedule) (string, error) {
	hasher := sha256.New()

	b, err := json.Marshal(schedule)

	if err != nil {
		return "", err
	}

	hasher.Write(b)
	hash := base64.URLEncoding.EncodeToString(hasher.Sum(nil))
	return hash, nil
}
