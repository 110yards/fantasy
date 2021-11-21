import * as client from "./client"

export const register = async command => {
  return client.post(null, "/user/register/email", command)
}

export const getProfile = async user => {
  return client.get(user, "/user/current")
}

export const updateProfile = async command => {
  return client.put(null, "/user/profile", command)
}

export const signIn = async user => {
  return client.post(user, "/user/signin")
}

export const userExists = async email => {
  return client.post(null, "/user/exists", { email: email })
}
