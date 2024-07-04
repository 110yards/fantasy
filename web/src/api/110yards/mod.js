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

export const updatePlayerGame = async command => {
  return client.post(null, "/mod/update_player_game", command)
}

export const revertPlayerGame = async command => {
  return client.post(null, "/mod/revert_player_game", command)
}
