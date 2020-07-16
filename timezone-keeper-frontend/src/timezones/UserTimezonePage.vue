<template>
    <div>
        <h2 v-if="timezone_to_update">{{timezone_to_update}}</h2>
        <h2 v-if="timezone_to_update">Update Timezone</h2>
        <h2 v-else>Create a new Timezone</h2>
        <form @submit.prevent="handleSubmit">
            <div class="form-group">
                <label for="TimezoneName">Timezone Name</label>
                <input type="text" v-model="name" :placeholder="[[ timezone_to_update.name ]]" v-validate="{ required: true, min: 3}" name="name" class="form-control" :class="{ 'is-invalid': submitted && errors.has('TimezoneName') }" />
                <div v-if="submitted && errors.has('TimezoneName')" class="invalid-feedback">{{ errors.first('TimezoneName') }}</div>
            </div>
            <div class="form-group">
                <select v-model="selected">
                    <option>Select Timezone</option>
                    <option v-for="timezone in timezones.timezones.items" :key="timezone.id" v-bind:value="{id: timezone.id}">{{timezone.location}}, {{timezone.city}}, {{timezone.relative_to_gmt}}</option>
                </select>
            </div>
            <div class="form-group">
                <button v-if="timezone_to_update" class="btn btn-primary" :disabled="timezones.status.updated">Update</button>
                <button v-else class="btn btn-primary" :disabled="timezones.status.created">Create</button>
                <router-link to="/" class="btn btn-link">Cancel</router-link>
            </div>
        </form>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
    data () {
        return {
            name: '',
            selected: '',
            submitted: false,
            timezone_to_update: false
        }
    },
    computed: {
        ...mapState({
            account: state => state.account,
            timezones: state => state.timezones
        })
    },
    created () {
        this.getAllTimezones();
        if(this.$route.query.timezone_to_update) {
            this.timezone_to_update = this.$route.query.timezone_to_update;
        }
    },
    methods: {
        ...mapActions('timezones', {
            getAllTimezones: 'getAll',
            createTimezone: 'create',
            updateTimezone: 'update'
        }),
        handleSubmit(e) {
            this.submitted = true;
            this.$validator.validate().then(valid => {
                if (valid) {
                    if (this.timezone_to_update) {
                        this.updateTimezone({name: this.timezone_to_update.name, timezone: {name: this.name, timezone_id: this.selected.id}});
                    } else {
                         this.createTimezone({name: this.name, timezone_id: this.selected.id});
                    }
                }
            });
        }
    }
};
</script>