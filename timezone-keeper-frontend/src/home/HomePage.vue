<template>
    <div>
        <p>
            <button class="btn btn-primary" v-on:click="$router.push('/login')">Logout</button>
            <button class="btn btn-primary" v-on:click="$router.push('/user')">Account</button>
        </p>
        <h1>Hi {{username}}!</h1>
        <p>You're logged in</p>
        <p>
            <button class="btn btn-primary" v-on:click="$router.push('/timezone')">Add a Timezone</button>
        </p>
        <h3 v-if="timezones.user_timezones">Here are your monitored timezones</h3>
        <ul v-if="timezones.user_timezones">
            <li v-for="tz in timezones.user_timezones" :key="tz.id">
                {{tz.name + ':   ' + tz.location + ' ' + tz.city + ' ' +tz.relative_to_gmt}}
                <span v-if="tz.deleting"><em> - Deleting...</em></span>
                <span v-else-if="tz.deleteError" class="text-danger"> - ERROR: {{tz.deleteError}}</span>
                <span v-else> - <a @click="deleteTimezone(tz.name)" class="text-danger">Delete</a></span>
                <span v-if="tz.updating"><em> - Updating...</em></span>
                <span v-else-if="tz.updateError" class="text-danger"> - ERROR: {{tz.deleteError}}</span>
                <span v-else> - <a @click="updateTimezone(tz)" class="text-danger">Update</a></span>
            </li>
        </ul>

    </div>
</template>


<script>
import { mapState, mapActions } from 'vuex'

export default {
    data () {
        return {
            username: ''
        }
    },
    computed: {
        ...mapState({
            account: state => state.account,
            timezones: state => state.timezones
        })
    },
    created () {
        this.getAllTimezonesForUser();
        this.username = JSON.parse(localStorage.getItem('user'))['username'];
    },
    methods: {
        ...mapActions('timezones', {
            getAllTimezonesForUser: 'getAllByUsername',
            createTimezone: 'create',
            deleteTimezone: 'delete'
        }),
        updateTimezone(timezone) {
            this.$router.push({path: '/timezone', query: { timezone_to_update: timezone}})
        }
    }
};
</script>
