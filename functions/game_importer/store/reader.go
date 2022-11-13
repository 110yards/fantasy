package store

import "context"

func ReadPath(ctx context.Context, path string, target interface{}) error {
	ref := RTDB.NewRef(path)
	return ref.Get(ctx, &target)
}

func SetPath(ctx context.Context, path string, value interface{}) error {
	ref := RTDB.NewRef(path)
	return ref.Set(ctx, value)
}
