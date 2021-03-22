<template>
  <div class="flex flex-center">
    <amplify-authenticator/>
  </div>
</template>

<script>
import { onAuthUIStateChange } from '@aws-amplify/ui-components'

export default {
  name: 'PageLogin',
  created () {
    this.unsubscribeAuth = onAuthUIStateChange(async (authState, authData) => {
      if (authState === 'signedin' && !this.loggedIn) {
        this.loggedIn = true
        // Todo: Vuex data
        await this.$router.push('/')
      }
    })
  },
  data () {
    return {
      unsubscribeAuth: null,
      loggedIn: false
    }
  },
  beforeDestroy () {
    this.unsubscribeAuth()
  }
}
</script>

<style scoped>

</style>
