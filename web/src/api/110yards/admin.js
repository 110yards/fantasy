import * as client from "./client"

export const problems = async () => {
  return client.get(null, "/admin/problems")
}

export const updatePlayers = async () => {
  return client.post(null, "/admin/update_players")
}

export const updateGames = async simState => {
  return client.post(null, "/admin/update_games", simState)
}

export const endOfDay = async () => {
  return client.post(null, "/admin/end_of_day")
}

export const resetWeekEnd = async () => {
  return client.post(null, "/admin/reset_week_end")
}

export const updateSchedule = async command => {
  return client.post(null, "/admin/schedule", command)
}
