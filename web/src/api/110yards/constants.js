export const draftState = {
  NotStarted: "not_started",
  InProgress: "in_progress",
  Complete: "completed",
  Reset: "reset",
}

export const draftType = {
  Snake: "snake",
  Auction: "auction",
  Commissioner: "commissioner",
}

export const positionType = {
  Bench: "bench",
  Bye: "bye",
  DFlex: "d-flex",
  DB: "db",
  DL: "dl",
  Flex: "flex",
  IR: "ir",
  K: "k",
  LB: "lb",
  OFlex: "o-flex",
  QB: "qb",
  RB: "rb",
  WR: "wr",

  spotName: type => {
    // TODO: 2022 - change flex abbreviations
    switch (type) {
      case positionType.OFlex:
        return "OF"
      case positionType.DFlex:
        return "DF"
      case positionType.Flex:
        return "F"
      case positionType.Bye:
        return "BYE"

      case positionType.Bench:
        return "BN"
    }

    return type.toUpperCase()
  },
}

export const visiblePlayerPositions = [
  positionType.QB,
  positionType.RB,
  positionType.WR,
  positionType.K,
  positionType.DB,
  positionType.DL,
  positionType.LB,
]

export const selectablePositions = [
  positionType.Bench,
  positionType.DFlex,
  positionType.DB,
  positionType.DL,
  positionType.Flex,
  positionType.K,
  positionType.LB,
  positionType.OFlex,
  positionType.QB,
  positionType.RB,
  positionType.WR,
]

export const playerStatus = {
  Out: "out",
  Probable: "probable",
  Questionable: "questionable",
  InjuredSixGames: "six-game",

  getText: status => {
    switch (status) {
      case playerStatus.InjuredSixGames:
        return "IL-6"
      case playerStatus.Questionable:
        return "Q"
      case playerStatus.Probable:
        return "P"
      case playerStatus.Out:
        return "OUT"
      default:
        return ""
    }
  },

  getSeverity: status => {
    switch (status) {
      case playerStatus.Out:
      case playerStatus.InjuredSixGames:
        return 3
      case playerStatus.Questionable:
        return 2
      case playerStatus.Probable:
        return 1
      default:
        return 0
    }
  },

  getFullText: status => {
    switch (status) {
      case playerStatus.Active:
        return "Active"
      case playerStatus.InjuredOneGame:
        return "1-Game Injured List"
      case playerStatus.InjuredSixGames:
        return "6-Game Injured List"
      case playerStatus.Suspended:
        return "Suspended"
      case playerStatus.PracticeSquad:
        return "Practice Squad"
      case playerStatus.Questionable:
        return "Questionable"
      case playerStatus.Probable:
        return "Probable"
      default:
        return "Not Active"
    }
  },
}

export const teamId = {
  FreeAgent: 0,
}

export const matchupType = {
  Regular: "regular",
  Playoff: "playoff",
  PlayoffBye: "playoff_bye",
  Loser: "loser",
  Championship: "championship",
}

export const eventStatus = {
  PreGame: "pre_game",
  InProgress: "in_progress",
  Final: "final",
  Postponed: "postponed",
  Cancelled: "cancelled",
}

export const waiverBidResult = {
  Unprocessed: 0,
  SuccessPending: 1,
  Success: 2,
  FailedDropPlayerNotOnRoster: -1,
  FailedNotEnoughMoney: -2,
  FailedNoRosterSpace: -3,
  FailedOutBid: -4,
  FailedLowerPriority: -5,

  getText: result => {
    switch (result) {
      case waiverBidResult.Success:
        return "Successful"

      case waiverBidResult.FailedDropPlayerNotOnRoster:
        return "Failed (drop player no longer on roster)"

      case waiverBidResult.FailedNotEnoughMoney:
        return "Failed (not enough money left)"

      case waiverBidResult.FailedNoRosterSpace:
        return "Failed (no space on roster)"

      case waiverBidResult.FailedOutBid:
        return "Failed (outbid)"

      case waiverBidResult.FailedLowerPriority:
        return "Failed (another bid had higher priority)"

      default:
        return "Failed (unknown reason)"
    }
  },
}

export const transactionType = {
  addPlayer: "add_player",
  claimPlayer: "claim_player",
  dropPlayer: "drop_player",
  changeRosterName: "change_roster_name",
  commissionerDropPlayer: "commissioner_drop_player",
  commissionerChangeRosterName: "commissioner_change_roster_name",
  commissionerChangeScoring: "commissioner_change_scoring",
  commissionerMovePlayer: "commissioner_move_player",
  commissionerAdjustResult: "commissioner_adjust_result",

  isCommissionerChange(trxType) {
    switch (trxType) {
      case transactionType.commissionerChangeRosterName:
      case transactionType.commissionerChangeScoring:
      case transactionType.commissionerDropPlayer:
      case transactionType.commissionerMovePlayer:
      case transactionType.commissionerAdjustResult:
        return true
      default:
        return false
    }
  },
}
