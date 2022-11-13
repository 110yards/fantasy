package publisher

var Instance Publisher

func Initialize(isDev bool) {
	if isDev {
		Instance = &virtualPublisher{}
	} else {
		Instance = &googlePublisher{}
	}
}
