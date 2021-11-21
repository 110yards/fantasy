import * as client from "./client"

export const rosterScore = async (leagueId, rosterId) => {
  return client.get(null, `/score/league/${leagueId}/roster/${rosterId}`)
}

export const playerScore = async (leagueId, playerId) => {
  return client.get(null, `/score/league/${leagueId}/player/${playerId}`)
}
