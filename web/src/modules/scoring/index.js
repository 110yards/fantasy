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
  // console.log(playerGames)

  if (!playerGames) return totalScore

  let playerGameArrays = Object.values(playerGames)
  // console.log(playerGameArrays)

  for (let playerGameArray of playerGameArrays) {
    // console.log(playerGameArray.length)
    if (playerGameArray.length == 0) continue

    // console.log(playerGameArray)
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

export const bindRosterScore = (vm, dataProp, weekNumber, roster) => {
  if (vm[dataProp] == null) {
    // needed?
    console.error("dataProp is null, initialize to {} before calling")
  }

  let season = vm.$root.currentSeason

  // add an observable property to hold the players
  vm.$set(vm[dataProp], "players", {})

  // add an observable property to hold the score
  vm.$set(vm[dataProp], "score", 0.0)

  // add a deep watch on dataProp.players; when it changes, recalculate dataProp.score
  vm.$watch(
    `${dataProp}.players`,
    function (newValue, _) {
      console.log("players changed: " + JSON.stringify(newValue))
      vm[dataProp].score = calculateRosterScore(vm.$root.leagueScoringSettings, newValue)
    },
    { deep: true },
  )

  let positions = Object.values(roster.positions)
  let players = positions.filter(x => x.player).map(x => x.player)
  let playerIds = players.map(x => x.id)

  for (let playerId of playerIds) {
    // add each player id as an observable property on dataProp.players
    vm.$set(vm[dataProp]["players"], playerId, null)
    // finally, bind to each player id property
    vm.$bind(`${dataProp}.players.${playerId}`, getPlayerGameRef(season, weekNumber, playerId))
  }
}
