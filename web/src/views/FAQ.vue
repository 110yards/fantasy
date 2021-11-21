<template>
  <v-card>
    <v-card-title class="">Frequently Asked Questions</v-card-title>

    <a name="nopasswords"></a>
    <v-card-title class="">Why does 110 yards use sign in links?</v-card-title>
    <v-card-text>
      <p>
        Passwords are insecure, and I don't want it to be my fault that your password is exposed if my provider (Google)
        is compromised.
      </p>
      <p>With password-less sign in, all you have to remember is your email.</p>
    </v-card-text>

    <a name="social"></a>
    <v-card-title class="">Why does 110 yards use social media providers to sign in?</v-card-title>
    <v-card-text>
      <p>
        So-called "Social login" or "3rd party login" is a quick an easy way to reduce the number of passwords that
        users need to remember.
      </p>
      <p>Using 3rd party login does not give 110 yards access to post on your behalf.</p>
      <p>3rd party login providers share the following information with 110yards:</p>
      <ul>
        <li>Your full name</li>
        <li>Your email address</li>
      </ul>
    </v-card-text>

    <a name="locks"></a>
    <v-card-title class="">When and why do players get locked? When do they get unlocked?</v-card-title>
    <v-card-text>
      <p>
        Players are locked at the beginning of their team's game for the week. Players whose team is on bye will be
        locked once the last game of the week has started
      </p>
      <p>
        All players remain locked until the last game of the week has completed, at which point, they become eligible
        for a <a href="#waivers">waiver bid</a>
        After waivers are processed, all players are unlocked until games start again.
      </p>
    </v-card-text>

    <a id="waivers" name="waivers"></a>
    <v-card-title>How do waivers work?</v-card-title>
    <v-card-text>
      <p>
        Waivers are used on this site as the method for adding players shortly after all games for the week have ended.
        Rather than making it a race to get the player who had the big week, while waivers are active, teams must place
        bids on available players.
      </p>
      <p>
        Bids are hidden from other teams, and bids of $0 are allowed (so you can always bid, even if you use up your
        entire waiver budget)
      </p>
      <p>
        At the end of waivers, the site will assign sort all of the bids from highest to lowest, then assign that player
        to the winning bidder's roster. In the case of a tie, the team with the highest
        <a href="#waiver-priority">waiver priority</a> will win.
      </p>
      <p>
        Bids can fail for several reasons:
      </p>
      <ul>
        <li>You get out bid by another manager</li>
        <li>You bid the same as another manager, but that manager has a worse record than you and wins on priority</li>
        <li>
          You bid the same as another manager, have higher priority to start than that manager, but have already won
          another bid, so your priority is lower now
        </li>
        <li>You don't select a drop player, and you have no room on your roster (maybe because you won another bid)</li>
        <li>
          You do select a drop player, but that player is no longer on your roster (maybe because you had two bids with
          him as the drop player)
        </li>
      </ul>

      <p>
        It's ok to make multiple bids which can't possibly work together, as a sort of back up plan. For example, you
        bid $5 on Player A, dropping Player C. Then you bid $4 on Player B, also dropping Player C. If you win the bid
        on Player A, your bid on player B will fail because C is no longer on your roster. If you lose the bid on Player
        A, you might still win the bid on Player B.
      </p>

      <p>
        Your pending waiver bids and the results from your past waiver bids can be seen on your roster page.
      </p>
    </v-card-text>

    <a name="waiver-priority"></a>
    <v-card-title>Waiver priority? What's that?</v-card-title>
    <v-card-text>
      <p>
        League rankings at the end of the week are used to assign waiver priority. The team with the worst record (in
        the case of a tie, <a href="#tie-breakers">tie breakers will be used</a>) gets the highest waiver priority, and
        so on down the list.
      </p>
      <p>
        Each time a team wins a waiver bid, they are moved to the bottom of the waiver priority list.
      </p>
      <p>
        E.g. Bob and Joe both bid $5 on the same two players. Bob has the worst record in his league, so his $5 for
        player 1 is accepted. Next, when the system looks at their bids on player 2, they are tied again, but now Joe
        has higher waiver priority, so his bid for player 2 is accepted.
      </p>
    </v-card-text>

    <a name="tie-breakers"></a>
    <v-card-title>Tie breakers</v-card-title>
    <v-card-text>
      <p>
        Rankings are calculated using the same "points" method as the CFL users. 2 points for a win, 1 point for a tie.
      </p>
      <p>Tie breakers are used to calculate rankings in the league if win-loss alone isn't enough.</p>
      <p>The following tie breakers are used, in this order:</p>
      <ol>
        <li>Total wins</li>
        <li>Player points for</li>
        <li>Player points differential (points for - points against)</li>
        <li>Random selection</li>
      </ol>
    </v-card-text>
  </v-card>
</template>
