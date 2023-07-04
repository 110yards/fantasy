import { format, formatRelative } from "date-fns"

export const formatScore = score => {
  return new Intl.NumberFormat("en-CA", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(score)
}

export const relativeDateTime = date => {
  return formatRelative(date, new Date())
}

export const birthDate = date => {
  return format(date, "MMMM d, yyyy")
}

export const shortDate = date => {
  return format(date, "MMM d")
}

export const longDate = date => {
  return format(date, "MMMM d")
}

export const shortTime = date => {
  return format(date, "h:mm a")
}

export const gameStartTime = (date, short) => {
  let f = short ? "eee H:mm" : "eee h:mma"
  return format(date, f)
}

export const shortName = player => {
  return `${player.first_name[0]}. ${player.last_name}`
}
