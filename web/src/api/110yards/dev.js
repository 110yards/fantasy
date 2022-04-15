import * as client from "./client"

export const processPubSub = async () => {
  return client.post(null, "/dev/pubsub")
}
