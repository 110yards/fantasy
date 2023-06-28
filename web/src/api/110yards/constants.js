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

/*
    Probable = "probable"
    Questionable = "questionable"
    Out = "out"
    InjuredSixGames = "six-game"
*/
export const playerStatus = {
  Out: "out",
  InjuredSixGames: "six-game",
  Questionable: "questionable",
  Probable: "probable",

  getText: status => {
    switch (status) {
      case playerStatus.Out:
        return "O"
      case playerStatus.InjuredSixGames:
        return "IL-6"
      case playerStatus.Questionable:
        return "Q"
      case playerStatus.Probable:
        return "P"
      default:
        return "O"
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
      case playerStatus.Out:
        return "Out"
      case playerStatus.InjuredSixGames:
        return "6-Game Injured List"
      case playerStatus.Questionable:
        return "Questionable"
      case playerStatus.Probable:
        return "Probable"
      default:
        return "Not active"
    }
  },
}

export const teams = {
  BC: "bc",
  CGY: "cgy",
  EDM: "edm",
  HAM: "ham",
  MTL: "mtl",
  OTT: "ott",
  SSK: "ssk",
  TOR: "tor",
  WPG: "wpg",

  getFullName: team => {
    switch (team) {
      case teams.BC:
        return "BC Lions"
      case teams.CGY:
        return "Calgary Stampeders"
      case teams.EDM:
        return "Edmonton Elks"
      case teams.HAM:
        return "Hamilton Tiger-Cats"
      case teams.MTL:
        return "Montreal Alouettes"
      case teams.OTT:
        return "Ottawa Redblacks"
      case teams.SSK:
        return "Saskatchewan Roughriders"
      case teams.TOR:
        return "Toronto Argonauts"
      case teams.WPG:
        return "Winnipeg Blue Bombers"
    }
  },
}

export const matchupType = {
  Regular: "regular",
  Playoff: "playoff",
  PlayoffBye: "playoff_bye",
  Loser: "loser",
  Championship: "championship",
}

export const eventStatus = {
  PreGame: "scheduled",
  InProgress: "active",
  Final: "complete",
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

  isCommissionerChange(trxType) {
    switch (trxType) {
      case transactionType.commissionerChangeRosterName:
      case transactionType.commissionerChangeScoring:
      case transactionType.commissionerDropPlayer:
      case transactionType.commissionerMovePlayer:
        return true
      default:
        return false
    }
  },
}
