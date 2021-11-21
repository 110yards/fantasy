import axios from "axios"
import eventBus from "../../modules/eventBus"
import store from "../../modules/store"

export const api110yardsUrl = process.env.VUE_APP_API_110_YARDS_URL

const instance = axios.create({
  baseURL: api110yardsUrl,
})

instance.interceptors.request.use(config => {
  eventBus.$emit("loading-start")
  return config
})

instance.interceptors.response.use(
  response => {
    eventBus.$emit("loading-stop")

    if (response.data && typeof response.data === "object" && "success" in response.data && !response.data.success) {
      eventBus.$emit("show-error", response.data.error)
    }

    return response
  },
  error => {
    eventBus.$emit("loading-stop")
    if (error.response == undefined) {
      let exception = new Error(error.message)
      eventBus.$emit("nullResponse", exception)
      return
    }

    if (error.response.status >= 400) {
      eventBus.$emit("exception", error)
      return
    }

    let exception = new Error(error.response.data.message)
    exception.response = error.response

    throw exception
  },
)

// TODO: Remove user parameter and always get it from the store
async function getRequestOptions(user, method, path) {
  let headers = {}

  if (!user) {
    user = store.state.currentUser
  }

  if (user) {
    let token = await user.getIdToken()
    headers["Authorization"] = `Bearer ${token}`
  }

  return {
    url: path,
    method: method,
    headers: headers,
  }
}

export async function get(user, path) {
  let options = await getRequestOptions(user, "get", path)
  let response = await instance(options)
  return response ? response.data : null
}

export async function post(user, path, data) {
  let options = await getRequestOptions(user, "post", path)
  options.data = data
  let response = await instance(options)

  return response ? response.data : null
}

export async function put(user, path, data) {
  let options = await getRequestOptions(user, "put", path)
  options.data = data
  let response = await instance(options)

  return response ? response.data : null
}

export async function del(user, path) {
  let options = await getRequestOptions(user, "delete", path)
  return instance(options)
}
