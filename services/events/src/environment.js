function getRequiredVariable(key) {
  const value = process.env[key]
  if (!value) {
    throw new Error(`Environment variable ${key} is required`)
  }
  return value
}

function getOptionalVariable(key, defaultValue) {
  return process.env[key] || defaultValue
}

export const config = {
  mongo: {
    connectionString: getRequiredVariable("MONGO_CONNECTION_STRING"),
    databaseName: getOptionalVariable("MONGO_DATABASE_NAME", "110yards"),
  },
}
