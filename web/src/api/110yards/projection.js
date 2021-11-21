import * as client from "./client"

export const playerProjection = async (leagueId, playerId) => {
  return client.get(null, `/projection/league/${leagueId}/player/${playerId}`)
}
