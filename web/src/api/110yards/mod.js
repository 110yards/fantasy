import * as client from "./client"

export const addNewPlayer = async command => {
  return client.post(null, "/mod/add_new_player", command)
}

export const matchPlayer = async command => {
  return client.post(null, "/mod/match_player", command)
}

export const updateGameData = async gameId => {
  return client.post(null, `/mod/update_game_data/${gameId}`, null)
}
