package updater

import (
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
)

func CalculateHash(game Game) (string, error) {
	hasher := sha256.New()

	b, err := json.Marshal(game)

	if err != nil {
		return "", err
	}

	hasher.Write(b)
	hash := base64.URLEncoding.EncodeToString(hasher.Sum(nil))
	return hash, nil
}
