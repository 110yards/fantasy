<template>
    <div v-if="player">
        {{ player.display_name }}
    </div>
</template>

<script>

import { firestore } from "../../../modules/firebase/index.js"

export default {
    name: "ReviewPlayer",
    props: {
        season: {
            type: Number,
            required: true,
        },
        playerGame: {
            type: Object,
            required: true,
        },
    },
    data() {
        return {
            player: null,
        }
    },
    methods: {

        async getPlayer() {
            if (this.season && this.playerGame) {
                let doc = await firestore.doc(`season/${this.season}/player/${this.playerGame.player_id}`).get()

                this.player = doc.data()
            }
        }
    },
    watch: {
        playerGame: {
            immediate: true,
            handler(v) {
                this.getPlayer()
            },
        },
        season: {
            immediate: true,
            handler(v) {
                this.getPlayer()
            },
        },
    }
}

</script>
