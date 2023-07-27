import * as client from "./client"

export const updateRosterName = async command => {
  return client.put(null, "/roster/name", command)
}

export const setNameChangeBan = async command => {
  return client.put(null, "/roster/name_change_ban", command)
}

export const dropPlayer = async command => {
  return client.post(null, "/roster/drop", command)
}

export const addPlayer = async command => {
  return client.post(null, "/roster/add", command)
}

export const movePlayer = async command => {
  return client.post(null, "/roster/move", command)
}

export const cancelBid = async command => {
  return client.post(null, "/roster/cancel_bid", command)
}

export const progress = async (leagueId, rosterId) => {
  return client.post(null, "/roster/progress", { league_id: leagueId, roster_id: rosterId })
}

export const setWaiverBudget = async command => {
  return client.put(null, "/roster/waiver_budget", command)
}

export const transferOwnership = async command => {
  return client.put(null, "/roster/transfer_ownership", command)
}
