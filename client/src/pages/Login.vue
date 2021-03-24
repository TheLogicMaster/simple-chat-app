<template>
  <div class="flex flex-center">
    <amplify-authenticator>
      <amplify-sign-up
        slot="sign-up"
        :form-fields.prop="signupFields"
      ></amplify-sign-up>
      <amplify-sign-in
        slot="sign-in"
        :form-fields.prop="signInFields"
      ></amplify-sign-in>
    </amplify-authenticator>
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
        await this.$store.dispatch('login')
        await this.$router.push('/')
      }
    })
  },
  data () {
    return {
      unsubscribeAuth: null,
      loggedIn: false,
      signupFields: [
        { type: "username" },
        { type: "password" },
        {
          type: "email",
          required: true
        }
      ],
      signInFields: [
        {
          type: "username",
          placeholder: "Enter username or email"
        },
        { type: "password" }
      ]
    }
  },
  beforeDestroy () {
    this.unsubscribeAuth()
  }
}
</script>

<style scoped>

</style>
