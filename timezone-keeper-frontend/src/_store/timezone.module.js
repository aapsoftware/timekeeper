import { timezoneService } from '../_services';
import { router } from '../_helpers';

const state = {
    timezones: {},
    user_timezones: [],
    status: {}
};

const actions = {
    getAll({ commit }) {
        commit('getAllRequest');

        timezoneService.getAll()
            .then(
                timezones => commit('getAllSuccess', timezones),
                error => commit('getAllFailure', error)
            );
    },
    getAllByUsername({ commit }) {
        commit('getAllForUserRequest');

        timezoneService.getAllByUsername()
            .then(
                timezone => commit('getAllForUserSuccess', timezone),
                error => commit('getAllForUserFailure', error)
            );
    },
    create({ dispathc, commit }, timezone) {
        commit('createRequest');
        timezoneService.create(timezone)
            .then(
                new_timezone => {
                    commit('createSuccess', new_timezone );
                    // router.push('/');
                    router.go(-1)
                    setTimeout(() => {
                        // display success message after route change completes
                        dispatch('alert/success', 'Timezone added successfully', { root: true });
                    })
                },
                error => commit('createFailure', { error: error.toString() })
            );
    },
    delete({ commit }, name) {
        commit('deleteRequest', name);
        timezoneService.delete(name)
            .then(
                user => commit('deleteSuccess', name),
                error => commit('deleteFailure', { name: name, error: error.toString() })
            );
    },
    update({ dispatch, commit }, {name, timezone}) {
        commit('updateRequest', name);
        timezoneService.update(name, timezone)
            .then(
                user => {
                    commit('updateSuccess', name),
                    router.go(-1)
                    setTimeout(() => {
                        // display success message after route change completes
                        dispatch('alert/success', 'Timezone updated successfully', { root: true });
                    })
                },
                error => commit('updateFailure', { name: name, error: error.toString() })
            );
    }
};

const mutations = {
    getAllRequest(state) {
        state.status = { loading_timezones: true };
    },
    getAllSuccess(state, timezones) {
        state.timezones = { items: timezones['data'] };
        state.status = { loading_timezones_done: true };
    },
    getAllFailure(state, error) {
        state.status = { error };
        state.timezones = {};
        state.user_timezones = [];
    },
    getAllForUserRequest(state) {
        state.status = { loading_user_timezones: true };
    },
    getAllForUserSuccess(state, timezones) {
        state.user_timezones = timezones['data'];
        state.status = { loading_user_timezones_done: true };
    },
    getAllForUserFailure(state, error) {
        state.status = { error };
        state.user_timezones = [];
    },
    createRequest(state) {
        state.status = { creating: true };
    },
    createSuccess(state,  timezone) {
        state.status = { created: true };
        state.user_timezones.push(timezone);
    },
    createFailure(state, error) {
        state.status = {created: false };
    },
    deleteRequest(state, name) {
        // add 'deleting:true' property to timezone being deleted
        state.user_timezones = state.user_timezones.map(timezone =>
            timezone.name === name
                ? { ...timezone, deleting: true }
                : timezone
        )
    },
    deleteSuccess(state, name) {
        // remove deleted user from state
        state.user_timezones = state.user_timezones.filter(timezone => timezone.name !== name)
    },
    deleteFailure(state, { name, error }) {
        // remove 'deleting:true' property and add 'deleteError:[error]' property to user
        state.user_timezones = state.user_timezones.map(timezone => {
            if (timezone.name === name) {
                // make copy  without 'deleting:true' property
                const { deleting, ...userCopy } = timezone;
                // return copy  with 'deleteError:[error]' property
                return { ...userCopy, deleteError: error };
            }

            return user;
        })
    },
    updateRequest(state, name) {
        // add 'updating:true' property to timezone being updated
        state.user_timezones = state.user_timezones.map(timezone =>
            timezone.name === name
                ? { ...timezone, updating: true }
                : timezone
        )
    },
    updateSuccess(state, name) {
        // remove 'updating:true' property and add 'updateError:[error]' property to user
        state.user_timezones = state.user_timezones.map(timezone => {
            if (timezone.name === name) {
                // make copy without 'deleting:true' property
                const { updating, ...userCopy } = timezone;
                // return copy with 'updateError:[error]' property
                return { ...userCopy };
            }

            return timezone;
        })
        state.status = { updated: true };
    },
    updateFailure(state, { name, error }) {
        // remove 'updating:true' property and add 'updateError:[error]' property to user
        state.user_timezones = state.user_timezones.map(timezone => {
            if (timezone.name === name) {
                // make copy  without 'deleting:true' property
                const { updating, ...userCopy } = timezone;
                // return copy  with 'updateError:[error]' property
                return { ...userCopy, updateError: error };
            }

            return timezone;
        })
        state.status = {updated: false };
    }
};

export const timezones = {
    namespaced: true,
    state,
    actions,
    mutations
};
