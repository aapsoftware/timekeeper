<template>
    <div>
        <div v-if="updating">
            <h2>Update Account Details</h2>
            <div class="form-group">
                <label for="firstName">First Name</label>
                <input type="text" v-model="new_user.first_name" v-validate="{ min: 3 }" name="first_name" class="form-control" />
            </div>
            <div class="form-group">
                <label for="lastName">Last Name</label>
                <input type="text" v-model="new_user.last_name" v-validate="{ min: 3}" name="lastName" class="form-control" />
            </div>
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" v-model="new_user.username" v-validate="{ min: 6}" name="username" class="form-control"/>
            </div>
            <div class="form-group">
                <label for="email">email</label>
                <input type="text" v-model="new_user.email" v-validate="'email'" name="email" class="form-control" />
            </div>
            <div class="form-group">
                <label htmlFor="password">Password</label>
                <input type="password" v-model="new_user.password" v-validate="{ min: 8}" name="password" class="form-control" />
            </div>
            <div class="form-group">
                <button class="btn btn-primary" v-on:click="handleSubmit({updateSubmit: true})">Update</button>
                <button class="btn btn-primary" v-on:click="handleSubmit({cancel: true})">Cancel</button>
            </div>
        </div>
        <div v-else>
            <h2>Account Details</h2>
            <div class="form-group">
                <label for="firstName">First Name</label>
                <input type="text" disabled v-bind:value="user.first_name" name="first_name" class="form-control" />
            </div>
            <div class="form-group">
                <label for="firstName">Last Name</label>
                <input type="text" disabled v-bind:value="user.last_name" name="last_name" class="form-control" />
            </div>
            <div class="form-group">
                <label for="firstName">Username</label>
                <input type="text" disabled v-bind:value="user.username" name="username" class="form-control" />
            </div>
            <div class="form-group">
                <label for="firstName">Email</label>
                <input type="text" disabled v-bind:value="user.email" name="email" class="form-control" />
            </div>
            <div class="form-group">
                <label for="firstName">Role</label>
                <input type="text" disabled v-bind:value="user.role" name="role" class="form-control" />
            </div>
            <div class="form-group">
                <button class="btn btn-primary" v-on:click="handleSubmit({update: true})">Update Details</button>
                <button class="btn btn-primary" v-on:click="$router.push('/home')">Home</button>
            </div>
        </div>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
    data () {
        return {
            updating: false,
            new_user: {
                first_name: '',
                last_name: '',
                username: '',
                password: '',
                email: ''
            },
            user: {}
        }
    },
    computed: {
        ...mapState({
            users: state => state.users
        })
    },
    created () {
        this.user = this.users.user;
    },
    methods: {
        ...mapActions('users', {
            updateUserDetails: 'updateUserDetails'
        }),
        handleSubmit(options) {
            if (options.update){
                this.updating = true;
            } else {
                if (options.updateSubmit){
                    this.$validator.validate().then(valid => {
                        if (valid) {
                            let filtered = Object.fromEntries(Object.entries(this.new_user).filter(([k,v]) => v!=''));
                            this.updateUserDetails(filtered);
                            this.user = {
                                ...this.user,
                                ...filtered
                            }
                        }
                    });
                }
                this.updating = false;
            }
        }
    }
};
</script>