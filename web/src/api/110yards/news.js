import * as client from "./client"

export const getNews = async () => {
  return client.get(null, `/news`)
}
