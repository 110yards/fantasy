package scheduler

const EventTypePreseason int = 0

func CreateSchedule(year int, games []Game) (Schedule, error) {
	m := make(map[int]Game)

	for _, g := range games {
		if g.EventType.EventTypeId == EventTypePreseason {
			g.Week *= -1
		}

		m[g.GameId] = g
	}

	schedule := Schedule{
		Season: year,
		Games:  m,
	}

	hash, err := CalculateHash(schedule)
	schedule.Hash = hash
	return schedule, err
}
