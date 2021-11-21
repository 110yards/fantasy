<template>
  <div>
    <h1 class="brand">110 yards</h1>
    <h5 v-if="enablePublicLeagues">Find a public league, or enter a private league code.</h5>
    <h5 v-else>Enter private league code and password if required</h5>

    <section class="row">
      <div class="col-12">
        <h5 v-if="enablePublicLeagues">Join a private league</h5>
        <div class="row">
          <div class="col-12">
            <join-private-form />
          </div>
        </div>
      </div>
    </section>
    <hr />

    <section class="row" v-if="enablePublicLeagues">
      <div class="col-12">
        <h4>Join a public league</h4>
        <table class="table">
          <thead>
            <tr>
              <th>League Name</th>
              <th>Teams</th>
              <th>Draft Date</th>
              <th>Scoring</th>
              <th></th>
            </tr>
          </thead>
          <!-- @foreach (var league in Model)
		{
			<tr>
				<td>@league.LeagueName</td>
				<td>@league.Managers.Count()</td>
				<td></td>
				<td><a href="@Url.Action("ViewScoring", "League", new { leagueId = league.Id })" target="_blank">View</a></td>
				<td><a href="@Url.Action("AcceptInvite", "League", new { leagueId = league.Id })" class="btn btn-default">Join league</a></td>
			</tr>
          }-->
        </table>
      </div>
    </section>
  </div>
</template>

<script>
import JoinPrivateForm from "../../components/league/JoinPrivateForm.vue"

export default {
  name: "join-league",
  components: {
    JoinPrivateForm,
  },

  computed: {
    enablePublicLeagues() {
      return this.$root.enablePublicLeagues
    },
  },
}
</script>
