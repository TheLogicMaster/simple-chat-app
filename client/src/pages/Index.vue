<template>
  <q-page class="flex flex-center">

  </q-page>
</template>

<script>

import { API } from '@aws-amplify/api'

export default {
  name: 'PageIndex',
  mounted () {
    API
      .post('api', '', { // OPTIONAL
        headers: {}, // OPTIONAL
        body: {
          conversation: '1234'
        },
        response: true, // OPTIONAL (return the entire Axios response object instead of only response.data)
        queryStringParameters: {  // OPTIONAL
          name: 'param',
        },
      })
      .then(response => {
        console.log(response)
      })
      .catch(error => {
        console.log(error.response);
      });
  }
}
</script>
