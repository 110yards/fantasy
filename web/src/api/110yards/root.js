import * as client from "./client"

export const status = async background => {
  if (background) {
    return fetch(`${client.api110yardsUrl}/`)
  } else {
    return client.get(null, "/")
  }
}
