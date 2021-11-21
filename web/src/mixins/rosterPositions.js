import { playerStatus } from "../api/110yards/constants"
import { firestore } from "../modules/firebase"

export default {
  data() {
    return {
      positionsConfig: null,
    }
  },

  computed: {
    activePositions() {
      if (this.positionsConfig == null) {
        return []
      } else {
        return this.positionsConfig.filter(v => this.isActivePosition(v))
      }
    },

    reservePositions() {
      if (this.positionsConfig == null) {
        return []
      } else {
        return this.positionsConfig.filter(v => this.isReservePosition(v))
      }
    },

    positionsConfigById() {
      if (this.positionsConfig == null) {
        return {}
      } else {
        return this.positionsConfig.reduce((obj, item) => ((obj[item.api_id || item.id] = item), obj), {})
      }
    },
  },

  methods: {
    isActivePosition(position) {
      return position.id != "bench" && !position.reserve
    },

    isReservePosition(position) {
      return position.reserve
    },

    isBenchPosition(position) {
      return position.id == "bench"
    },

    isActivePositionType(positionType) {
      if (!(positionType in this.positionsConfigById)) {
        return false
      } else {
        return this.isActivePosition(this.positionsConfigById[positionType])
      }
    },

    isBenchPositionType(positionType) {
      if (!(positionType in this.positionsConfigById)) {
        return false
      } else {
        return this.isBenchPosition(this.positionsConfigById[positionType])
      }
    },

    isReservePositionType(positionType) {
      if (!(positionType in this.positionsConfigById)) {
        return false
      } else {
        return this.isReservePosition(this.positionsConfigById[positionType])
      }
    },

    playerIsEligibleForPosition(player, positionType) {
      // TODO: need to remove these hard codes
      let playerPosition = player.position

      if (positionType == "bench") return true

      if (playerPosition == positionType) return true

      if (positionType == "ir") {
        return this.$root.enableRelaxedIR || player.status_current != playerStatus.Active
      }

      if (positionType == "bye") {
        let opponent = this.$root.getOpponent(player.team.abbreviation)
        return opponent == "BYE"
      }

      switch (playerPosition) {
        case "rb":
        case "wr":
        case "k":
          return ["flex", "o-flex"].includes(positionType)

        case "dl":
        case "db":
        case "lb":
          return ["flex", "d-flex"].includes(positionType)
      }

      return false
    },

    eligiblePlayerPositions(positionType) {
      let positionConfig = this.positionsConfigById[positionType]

      if (positionConfig.is_player_position) return [positionType]

      // hate this hard code - TODO: put this in the firebase config
      let id = positionConfig.api_id || positionConfig.id // TODO(next year): Fix the mismatch between o_flex and o-flex
      switch (id) {
        case "flex":
          return ["k", "rb", "wr", "db", "dl", "lb"]

        case "d-flex":
          return ["db", "dl", "lb"]

        case "o-flex":
          return ["k", "rb", "wr"]

        default:
          return []
      }
    },
  },
  created() {
    this.$bind("positionsConfig", firestore.collection("roster-positions").orderBy("order"))
  },
}
