package publisher

var Instance Publisher

func Initialize(isDev bool, projectId string) {
	if isDev {
		Instance = &virtualPublisher{}
	} else {
		Instance = &googlePublisher{
			projectId: projectId,
		}
	}
}
