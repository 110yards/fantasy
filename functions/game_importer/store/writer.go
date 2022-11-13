package store

import "context"

func SetPath(ctx context.Context, path string, value interface{}) error {
	ref := RTDB.NewRef(path)
	return ref.Set(ctx, value)
}
