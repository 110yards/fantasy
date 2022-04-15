import { firestore } from "../firebase"

export const calculate = (scoring, stats) => {
  let totalScore = 0.0

  for (let key in scoring) {
    if (key == "id") continue

    if (!(key in stats)) continue

    let stat = stats[key]
    let value = scoring[key]

    let score = !!stat ? stat * value : 0
    totalScore += score
  }

  return totalScore
}

export const calculateMultiple = (scoring, playerGames) => {
  let totalScore = 0.0

  for (let playerGame of playerGames) {
    totalScore += calculate(scoring, playerGame.stats)
  }

  return totalScore
}

export const calculateRosterScore = (scoring, playerGames) => {
  let totalScore = 0.0

  if (!playerGames) return totalScore

  let playerGameArrays = Object.values(playerGames)

  for (let playerGameArray of playerGameArrays) {
    if (playerGameArray.length == 0) continue

    let game = playerGameArray[0]
    console.log(game)
    totalScore += calculate(scoring, game.stats)
  }

  return totalScore
}

export const getRosterScoreRef = (season, weekNumber, roster) => {
  let positions = Object.values(roster.positions)
  let players = positions.filter(x => x.player).map(x => x.player)
  let playerIds = players.map(x => x.id)

  let path = `season/${season}/player_game/`
  let ref = firestore
    .collection(path)
    .where("week_number", "==", parseInt(weekNumber))
    .where("player_id", "in", playerIds)

  return ref
}

export const getPlayerGameRef = (season, weekNumber, playerId) => {
  let path = `season/${season}/player_game`
  let ref = firestore
    .collection(path)
    .where("week_number", "==", parseInt(weekNumber))
    .where("player_id", "==", playerId)

  return ref
}
