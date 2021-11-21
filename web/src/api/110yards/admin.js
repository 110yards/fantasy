import * as client from "./client"

export const problems = async () => {
  return client.get(null, "/admin/problems")
}
