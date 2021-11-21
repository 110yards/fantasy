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

  return totalScore.toFixed(2)
}
