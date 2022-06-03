import * as client from "./client"

export const create = async (user, league) => {
  return client.post(user, "/league", league)
}

export const update = async (user, leagueId, options) => {
  return client.put(user, `/league/${leagueId}`, options)
}

export const join = async (user, leagueId, password) => {
  return client.post(user, `/league/${leagueId}/join/`, {
    password: password,
  })
}

export const closeRegistration = async (user, leagueId) => {
  return client.put(user, `/league/${leagueId}/registration/close`)
}

export const openRegistration = async (user, leagueId) => {
  return client.put(user, `/league/${leagueId}/registration/open`)
}

export const updateRosterPositions = async (user, leagueId, rosterPositions) => {
  return client.put(user, `/league/${leagueId}/positions`, rosterPositions)
}

export const updateScoringConfig = async (leagueId, scoring) => {
  return client.put(null, `/league/${leagueId}/scoring`, scoring)
}

export const removeRoster = async (user, leagueId, rosterId) => {
  return client.del(user, `/league/${leagueId}/roster/${rosterId}`)
}

export const generateSchedule = async (user, leagueId, options) => {
  return client.put(user, `/league/${leagueId}/schedule`, options)
}

export const beginDraft = async (user, leagueId) => {
  return client.post(user, `/league/${leagueId}/draft`)
}

export const updateDraftOrder = async (user, leagueId, order) => {
  return client.put(user, `/league/${leagueId}/draft_order`, order)
}

export const nominateForAuction = async (user, league_id, command) => {
  return client.post(user, `/league/${league_id}/draft/nominate`, command)
}

export const bidOnAuction = async (user, league_id, command) => {
  return client.post(user, `/league/${league_id}/draft/bid`, command)
}

export const passBidOnAuction = async (user, league_id, command) => {
  return client.post(user, `/league/${league_id}/draft/pass`, command)
}

export const pauseDraft = async (user, league_id) => {
  return client.post(user, `/league/${league_id}/draft/pause`)
}

export const resumeDraft = async (user, league_id) => {
  return client.post(user, `/league/${league_id}/draft/resume`)
}

export const undoLastPick = async (user, league_id) => {
  return client.post(user, `/league/${league_id}/draft/undo`)
}

export const selectPlayer = async (user, league_id, command) => {
  return client.post(user, `/league/${league_id}/draft/select_player`, command)
}

export const resetDraft = async league_id => {
  return client.del(null, `/league/${league_id}/draft`)
}

export const endDraft = async league_id => {
  return client.post(null, `/league/${league_id}/draft/end`)
}

export const fixSubscriptions = async command => {
  return client.post(null, `/league/fix_subscriptions`, command)
}

export const testDiscord = async (league_id, webhook_url) => {
  return client.post(null, `league/${league_id}/test_discord?webhook_url=${webhook_url}`)
}

export const getPlayerDetails = async (season, league_id, player_id) => {
  return client.get(null, `league/${league_id}/player/${player_id}/${season}`)
}

export const renewLeague = async leagueId => {
  return client.post(null, `league/${leagueId}/renew/`)
}

export const setNotes = async (user, leagueId, command) => {
  return client.put(user, `/league/${leagueId}/notes`, command)
}

export const getPlayersRef = async leagueId => {
  return client.get(null, `/league/${leagueId}/players`)
}
