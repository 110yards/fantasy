import express from "express"
const app = express()
import { createServer } from "http"
const server = createServer(app)
import { Server } from "socket.io"
const io = new Server(server)
import { startMongo } from "./mongo.js"

app.get("/healthz", (req, res) => {
  res.send({
    serviceName: "events",
    checks: {
      service: "OK",
    },
  })
})

io.on("connection", socket => {
  console.log("a user connected")
})

server.listen(3000, () => {
  console.log("listening on *:3000")
})

startMongo().catch(console.dir)
