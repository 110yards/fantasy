import * as client from "./client"

export const playerProjection = async (leagueId, playerId) => {
  return client.get(null, `/projection/league/${leagueId}/player/${playerId}`)
}

export const rosterProjection = async (leagueId, rosterId) => {
  return client.get(null, `/projection/league/${leagueId}/roster/${rosterId}`)
}
