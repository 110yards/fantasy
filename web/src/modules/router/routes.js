import Home from "../../views/Home.vue"
import FAQ from "../../views/FAQ.vue"
import DefaultError from "../../views/error/Default.vue"
import NotAuthorized from "../../views/error/NotAuthorized.vue"
import Admin from "../../views/admin/Admin.vue"
import Profile from "../../views/Profile.vue"

import Login from "../../views/auth/Login.vue"
import Register from "../../views/auth/Register.vue"
import PasswordLess from "../../views/auth/Passwordless.vue"

import CreateLeague from "../../views/league/Create.vue"
import LeagueIndex from "../../views/league/Index.vue"
import Join from "../../views/league/Join.vue"
import JoinDirect from "../../views/league/JoinDirect.vue"
import Matchup from "../../views/league/matchup/Matchup.vue"
import Roster from "../../views/league/roster/Roster.vue"
import Draft from "../../views/league/draft/Draft.vue"
import LeagueSettings from "../../views/league/LeagueSettings.vue"
import LeagueSchedule from "../../views/league/LeagueSchedule.vue"
import LeagueAdmin from "../../views/league/AdminWaiverResults.vue"

import CommissionerIndex from "../../views/commissioner/Index.vue"

import Players from "../../views/player/Players.vue"
import PlayerDetails from "../../views/player/PlayerDetails.vue"

export const routes = [
  {
    path: "/",
    name: "home",
    component: Home,
    meta: { anonymous: true },
  },
  {
    path: "/faq",
    name: "faq",
    component: FAQ,
    meta: { anonymous: true },
  },
  {
    path: "/ohno",
    name: "error",
    component: DefaultError,
    meta: { anonymous: true },
  },
  {
    path: "/access-denied",
    name: "access-denied",
    component: NotAuthorized,
    meta: { anonymous: true },
  },
  {
    path: "/login",
    name: "login",
    props: route => ({
      returnUrl: route.query.returnUrl,
    }),
    component: Login,
    meta: { anonymous: true },
  },
  {
    path: "/passwordless",
    name: "passwordless",
    component: PasswordLess,
    meta: { anonymous: true },
  },
  {
    path: "/signup",
    name: "signup",
    component: Register,
    meta: { anonymous: true },
  },
  {
    path: "/league/create",
    name: "create-league",
    component: CreateLeague,
  },
  {
    path: "/join",
    name: "join-league",
    component: Join,
  },
  {
    path: "/join/:joinId",
    name: "join-direct",
    props: true,
    component: JoinDirect,
  },
  {
    path: "/league/:leagueId",
    name: "league",
    props: true,
    component: LeagueIndex,
  },
  {
    path: "/league/:leagueId/week/:weekNumber/matchup/:matchupId",
    name: "matchup",
    component: Matchup,
    props: true,
  },
  {
    path: "/league/:leagueId/roster/:rosterId",
    name: "roster",
    props: true,
    component: Roster,
  },
  {
    path: "/league/:leagueId/players",
    name: "league-players",
    props: true,
    component: Players,
  },
  {
    path: "/league/:leagueId/player/:playerId",
    name: "league-player",
    props: true,
    component: PlayerDetails,
  },
  {
    path: "/league/:leagueId/draft",
    name: "draft",
    props: true,
    component: Draft,
  },
  {
    path: "/league/:leagueId/settings",
    name: "league-settings",
    props: true,
    component: LeagueSettings,
  },
  {
    path: "/league/:leagueId/schedule",
    name: "league-schedule",
    props: true,
    component: LeagueSchedule,
  },
  {
    path: "/league/:leagueId/admin",
    name: "league-admin",
    props: true,
    component: LeagueAdmin,
  },
  {
    path: "/commissioner/:leagueId",
    name: "commissioner",
    props: true,
    component: CommissionerIndex,
  },
  {
    path: "/admin",
    name: "admin",
    component: Admin,
    meta: { admin: true },
  },
  {
    path: "/profile",
    name: "profile",
    component: Profile,
  },
]
