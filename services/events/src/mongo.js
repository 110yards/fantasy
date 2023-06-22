import { MongoClient } from "mongodb"
import { config } from "./environment.js"

export const mongo = new MongoClient(config.mongo.connectionString)

export const startMongo = async () => {
  try {
    await mongo.connect()
    console.log("Connected successfully to MongoDB server")

    const db = mongo.db(config.mongo.databaseName)
    const collection = db.collection("messages")
    const changeStream = collection.watch()

    changeStream.on("change", next => {
      console.log(next)
    })

    console.log("Subscribed to message changes")
  } catch (err) {
    console.error(err)
    await mongo.close()
  }
}
